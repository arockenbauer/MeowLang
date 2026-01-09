use crate::ast::{ASTNode, LiteralValue};
use crate::error::{ErrorCatalog, MeowLangError};
use std::collections::HashMap;
use std::io::{self, Write};
use rand::Rng;
use std::thread;
use std::time::Duration;

#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    String(String),
    Number(f64),
    Integer(i64),
    Boolean(bool),
    List(Vec<Value>),
    Dict(HashMap<String, Value>),
    Function {
        params: Vec<String>,
        body: Vec<ASTNode>,
    },
    None,
}

impl Value {
    fn to_string(&self) -> String {
        match self {
            Value::String(s) => s.clone(),
            Value::Number(n) => n.to_string(),
            Value::Integer(i) => i.to_string(),
            Value::Boolean(b) => if *b { "vrai" } else { "faux" }.to_string(),
            Value::List(items) => {
                let strs: Vec<String> = items.iter().map(|v| v.to_string()).collect();
                format!("[{}]", strs.join(", "))
            },
            Value::Dict(_) => "<dictionnaire>".to_string(),
            Value::Function { .. } => "<fonction>".to_string(),
            Value::None => "".to_string(),
        }
    }
    
    fn to_number(&self) -> Result<f64, String> {
        match self {
            Value::Number(n) => Ok(*n),
            Value::Integer(i) => Ok(*i as f64),
            Value::String(s) => s.parse::<f64>().map_err(|_| format!("Cannot convert '{}' to number", s)),
            _ => Err("Cannot convert to number".to_string()),
        }
    }
    
    fn to_bool(&self) -> bool {
        match self {
            Value::Boolean(b) => *b,
            Value::Integer(i) => *i != 0,
            Value::Number(n) => *n != 0.0,
            Value::String(s) => !s.is_empty(),
            Value::List(l) => !l.is_empty(),
            Value::None => false,
            _ => true,
        }
    }
}

pub struct Interpreter {
    variables: HashMap<String, Value>,
    functions: HashMap<String, (Vec<String>, Vec<ASTNode>)>,
    filename: String,
    source_lines: Vec<String>,
    repeat_counter: Option<i64>,
}

impl Interpreter {
    pub fn new(filename: String, source_lines: Vec<String>) -> Self {
        Interpreter {
            variables: HashMap::new(),
            functions: HashMap::new(),
            filename,
            source_lines,
            repeat_counter: None,
        }
    }
    
    pub fn execute(&mut self, node: &ASTNode) -> Result<Value, MeowLangError> {
        match node {
            ASTNode::Program { statements, .. } => {
                let mut result = Value::None;
                for stmt in statements {
                    result = self.execute(stmt)?;
                }
                Ok(result)
            },
            
            ASTNode::Literal { value, .. } => {
                match value {
                    LiteralValue::String(s) => Ok(Value::String(s.clone())),
                    LiteralValue::Number(n) => Ok(Value::Number(*n)),
                    LiteralValue::Integer(i) => Ok(Value::Integer(*i)),
                    LiteralValue::Boolean(b) => Ok(Value::Boolean(*b)),
                    LiteralValue::None => Ok(Value::None),
                }
            },
            
            ASTNode::Identifier { name, position } => {
                if name == "compteur" {
                    if let Some(counter) = self.repeat_counter {
                        return Ok(Value::Integer(counter));
                    }
                }
                
                self.variables.get(name).cloned().ok_or_else(|| {
                    MeowLangError::new(
                        ErrorCatalog::get("E200"),
                        self.filename.clone(),
                        position.line,
                        position.column,
                    )
                    .with_extra("var_name".to_string(), name.clone())
                    .with_context(&self.source_lines)
                })
            },
            
            ASTNode::BinaryOp { left, operator, right, position } => {
                let left_val = self.execute(left)?;
                let right_val = self.execute(right)?;
                
                match operator.as_str() {
                    "+" => {
                        match (&left_val, &right_val) {
                            (Value::String(l), Value::String(r)) => Ok(Value::String(format!("{}{}", l, r))),
                            (Value::String(l), r) => Ok(Value::String(format!("{}{}", l, r.to_string()))),
                            (l, Value::String(r)) => Ok(Value::String(format!("{}{}", l.to_string(), r))),
                            _ => {
                                let l = left_val.to_number().map_err(|_| {
                                    MeowLangError::new(
                                        ErrorCatalog::get("E202"),
                                        self.filename.clone(),
                                        position.line,
                                        position.column,
                                    ).with_context(&self.source_lines)
                                })?;
                                let r = right_val.to_number().map_err(|_| {
                                    MeowLangError::new(
                                        ErrorCatalog::get("E202"),
                                        self.filename.clone(),
                                        position.line,
                                        position.column,
                                    ).with_context(&self.source_lines)
                                })?;
                                Ok(Value::Number(l + r))
                            }
                        }
                    },
                    "-" => {
                        let l = left_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        let r = right_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        Ok(Value::Number(l - r))
                    },
                    "*" => {
                        let l = left_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        let r = right_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        Ok(Value::Number(l * r))
                    },
                    "/" => {
                        let l = left_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        let r = right_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        
                        if r == 0.0 {
                            return Err(MeowLangError::new(
                                ErrorCatalog::get("E500"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines));
                        }
                        
                        Ok(Value::Number(l / r))
                    },
                    "%" => {
                        let l = left_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        let r = right_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        Ok(Value::Number(l % r))
                    },
                    "**" => {
                        let l = left_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        let r = right_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        Ok(Value::Number(l.powf(r)))
                    },
                    "=" => Ok(Value::Boolean(self.values_equal(&left_val, &right_val))),
                    "!=" => Ok(Value::Boolean(!self.values_equal(&left_val, &right_val))),
                    "<" => {
                        let l = left_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        let r = right_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        Ok(Value::Boolean(l < r))
                    },
                    ">" => {
                        let l = left_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        let r = right_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        Ok(Value::Boolean(l > r))
                    },
                    "<=" => {
                        let l = left_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        let r = right_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        Ok(Value::Boolean(l <= r))
                    },
                    ">=" => {
                        let l = left_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        let r = right_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        Ok(Value::Boolean(l >= r))
                    },
                    "et" => Ok(Value::Boolean(left_val.to_bool() && right_val.to_bool())),
                    "ou" => Ok(Value::Boolean(left_val.to_bool() || right_val.to_bool())),
                    _ => Err(MeowLangError::new(
                        ErrorCatalog::get("E100"),
                        self.filename.clone(),
                        position.line,
                        position.column,
                    ).with_context(&self.source_lines)),
                }
            },
            
            ASTNode::UnaryOp { operator, operand, position } => {
                let val = self.execute(operand)?;
                
                match operator.as_str() {
                    "-" => {
                        let n = val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })?;
                        Ok(Value::Number(-n))
                    },
                    "non" => Ok(Value::Boolean(!val.to_bool())),
                    _ => Err(MeowLangError::new(
                        ErrorCatalog::get("E100"),
                        self.filename.clone(),
                        position.line,
                        position.column,
                    ).with_context(&self.source_lines)),
                }
            },
            
            ASTNode::Assignment { name, value, .. } => {
                let val = self.execute(value)?;
                self.variables.insert(name.clone(), val.clone());
                Ok(val)
            },
            
            ASTNode::FunctionCall { name, arguments, position } => {
                self.execute_function_call(name, arguments, position)
            },
            
            ASTNode::IfStatement { condition, then_block, elif_blocks, else_block, .. } => {
                let cond_val = self.execute(condition)?;
                
                if cond_val.to_bool() {
                    let mut result = Value::None;
                    for stmt in then_block {
                        result = self.execute(stmt)?;
                    }
                    return Ok(result);
                }
                
                for (elif_cond, elif_body) in elif_blocks {
                    let elif_val = self.execute(elif_cond)?;
                    if elif_val.to_bool() {
                        let mut result = Value::None;
                        for stmt in elif_body {
                            result = self.execute(stmt)?;
                        }
                        return Ok(result);
                    }
                }
                
                if let Some(else_body) = else_block {
                    let mut result = Value::None;
                    for stmt in else_body {
                        result = self.execute(stmt)?;
                    }
                    return Ok(result);
                }
                
                Ok(Value::None)
            },
            
            ASTNode::WhileLoop { condition, body, .. } => {
                let mut result = Value::None;
                
                while self.execute(condition)?.to_bool() {
                    for stmt in body {
                        result = self.execute(stmt)?;
                    }
                }
                
                Ok(result)
            },
            
            ASTNode::RepeatLoop { count, body, .. } => {
                let count_val = self.execute(count)?;
                let n = count_val.to_number().map_err(|_| {
                    MeowLangError::new(
                        ErrorCatalog::get("E202"),
                        self.filename.clone(),
                        count.position().line,
                        count.position().column,
                    ).with_context(&self.source_lines)
                })? as i64;
                
                let mut result = Value::None;
                
                for i in 1..=n {
                    self.repeat_counter = Some(i);
                    for stmt in body {
                        result = self.execute(stmt)?;
                    }
                }
                
                self.repeat_counter = None;
                Ok(result)
            },
            
            ASTNode::ForEachLoop { iterator, iterable, body, position } => {
                let iterable_val = self.execute(iterable)?;
                
                let items = match iterable_val {
                    Value::List(ref items) => items.clone(),
                    _ => return Err(MeowLangError::new(
                        ErrorCatalog::get("E202"),
                        self.filename.clone(),
                        position.line,
                        position.column,
                    ).with_context(&self.source_lines)),
                };
                
                let mut result = Value::None;
                
                for item in items {
                    self.variables.insert(iterator.clone(), item);
                    for stmt in body {
                        result = self.execute(stmt)?;
                    }
                }
                
                Ok(result)
            },
            
            ASTNode::FunctionDef { name, parameters, body, .. } => {
                self.functions.insert(name.clone(), (parameters.clone(), body.clone()));
                Ok(Value::None)
            },
            
            ASTNode::ReturnStatement { value, .. } => {
                if let Some(val) = value {
                    self.execute(val)
                } else {
                    Ok(Value::None)
                }
            },
            
            ASTNode::ListNode { elements, .. } => {
                let mut items = Vec::new();
                for elem in elements {
                    items.push(self.execute(elem)?);
                }
                Ok(Value::List(items))
            },
            
            ASTNode::IndexAccess { object, index, position } => {
                let obj_val = self.execute(object)?;
                let index_val = self.execute(index)?;
                
                match obj_val {
                    Value::List(items) => {
                        let idx = index_val.to_number().map_err(|_| {
                            MeowLangError::new(
                                ErrorCatalog::get("E202"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            ).with_context(&self.source_lines)
                        })? as usize;
                        
                        items.get(idx).cloned().ok_or_else(|| {
                            MeowLangError::new(
                                ErrorCatalog::get("E700"),
                                self.filename.clone(),
                                position.line,
                                position.column,
                            )
                            .with_extra("index".to_string(), idx.to_string())
                            .with_extra("size".to_string(), items.len().to_string())
                            .with_context(&self.source_lines)
                        })
                    },
                    _ => Err(MeowLangError::new(
                        ErrorCatalog::get("E202"),
                        self.filename.clone(),
                        position.line,
                        position.column,
                    ).with_context(&self.source_lines)),
                }
            },
            
            ASTNode::TryExcept { try_block, except_block, .. } => {
                let mut result = Value::None;
                
                for stmt in try_block {
                    match self.execute(stmt) {
                        Ok(val) => result = val,
                        Err(_) => {
                            for stmt in except_block {
                                result = self.execute(stmt)?;
                            }
                            return Ok(result);
                        }
                    }
                }
                
                Ok(result)
            },
            
            ASTNode::ExpressionStatement { expression, .. } => {
                self.execute(expression)
            },
            
            _ => Ok(Value::None),
        }
    }
    
    fn values_equal(&self, left: &Value, right: &Value) -> bool {
        match (left, right) {
            (Value::String(l), Value::String(r)) => l == r,
            (Value::Integer(l), Value::Integer(r)) => l == r,
            (Value::Number(l), Value::Number(r)) => (l - r).abs() < f64::EPSILON,
            (Value::Boolean(l), Value::Boolean(r)) => l == r,
            (Value::None, Value::None) => true,
            _ => false,
        }
    }
    
    fn execute_function_call(&mut self, name: &str, arguments: &[ASTNode], position: &crate::ast::Position) -> Result<Value, MeowLangError> {
        match name {
            "ecrire" => {
                let mut output = String::new();
                for (i, arg) in arguments.iter().enumerate() {
                    let val = self.execute(arg)?;
                    if i > 0 {
                        output.push(' ');
                    }
                    output.push_str(&val.to_string());
                }
                println!("{}", output);
                Ok(Value::None)
            },
            
            "demander_texte" => {
                if let Some(arg) = arguments.first() {
                    let prompt = self.execute(arg)?;
                    print!("{} ", prompt.to_string());
                    io::stdout().flush().unwrap();
                    
                    let mut input = String::new();
                    io::stdin().read_line(&mut input).unwrap();
                    Ok(Value::String(input.trim().to_string()))
                } else {
                    Ok(Value::String(String::new()))
                }
            },
            
            "demander_nombre" => {
                if let Some(arg) = arguments.first() {
                    let prompt = self.execute(arg)?;
                    print!("{} ", prompt.to_string());
                    io::stdout().flush().unwrap();
                    
                    let mut input = String::new();
                    io::stdin().read_line(&mut input).unwrap();
                    
                    let number = input.trim().parse::<f64>().unwrap_or(0.0);
                    Ok(Value::Number(number))
                } else {
                    Ok(Value::Number(0.0))
                }
            },
            
            "minuscule" => {
                if let Some(arg) = arguments.first() {
                    let val = self.execute(arg)?;
                    Ok(Value::String(val.to_string().to_lowercase()))
                } else {
                    Ok(Value::String(String::new()))
                }
            },
            
            "majuscule" => {
                if let Some(arg) = arguments.first() {
                    let val = self.execute(arg)?;
                    Ok(Value::String(val.to_string().to_uppercase()))
                } else {
                    Ok(Value::String(String::new()))
                }
            },
            
            "longueur" => {
                if let Some(arg) = arguments.first() {
                    let val = self.execute(arg)?;
                    match val {
                        Value::String(s) => Ok(Value::Integer(s.len() as i64)),
                        Value::List(items) => Ok(Value::Integer(items.len() as i64)),
                        _ => Ok(Value::Integer(0)),
                    }
                } else {
                    Ok(Value::Integer(0))
                }
            },
            
            "aleatoire" => {
                if arguments.len() >= 2 {
                    let start = self.execute(&arguments[0])?.to_number().unwrap_or(0.0) as i64;
                    let end = self.execute(&arguments[1])?.to_number().unwrap_or(100.0) as i64;
                    
                    let mut rng = rand::thread_rng();
                    let random_num = rng.gen_range(start..=end);
                    Ok(Value::Integer(random_num))
                } else {
                    Ok(Value::Integer(0))
                }
            },
            
            "sqrt" => {
                if let Some(arg) = arguments.first() {
                    let val = self.execute(arg)?;
                    let n = val.to_number().unwrap_or(0.0);
                    Ok(Value::Number(n.sqrt()))
                } else {
                    Ok(Value::Number(0.0))
                }
            },
            
            "abs" => {
                if let Some(arg) = arguments.first() {
                    let val = self.execute(arg)?;
                    let n = val.to_number().unwrap_or(0.0);
                    Ok(Value::Number(n.abs()))
                } else {
                    Ok(Value::Number(0.0))
                }
            },
            
            "round" => {
                if let Some(arg) = arguments.first() {
                    let val = self.execute(arg)?;
                    let n = val.to_number().unwrap_or(0.0);
                    Ok(Value::Integer(n.round() as i64))
                } else {
                    Ok(Value::Integer(0))
                }
            },
            
            "floor" => {
                if let Some(arg) = arguments.first() {
                    let val = self.execute(arg)?;
                    let n = val.to_number().unwrap_or(0.0);
                    Ok(Value::Integer(n.floor() as i64))
                } else {
                    Ok(Value::Integer(0))
                }
            },
            
            "ceil" => {
                if let Some(arg) = arguments.first() {
                    let val = self.execute(arg)?;
                    let n = val.to_number().unwrap_or(0.0);
                    Ok(Value::Integer(n.ceil() as i64))
                } else {
                    Ok(Value::Integer(0))
                }
            },
            
            "attendre" => {
                if let Some(arg) = arguments.first() {
                    let val = self.execute(arg)?;
                    let seconds = val.to_number().unwrap_or(0.0);
                    
                    if seconds < 0.0 {
                        return Err(MeowLangError::new(
                            ErrorCatalog::get("E800"),
                            self.filename.clone(),
                            position.line,
                            position.column,
                        )
                        .with_extra("duration".to_string(), seconds.to_string())
                        .with_context(&self.source_lines));
                    }
                    
                    thread::sleep(Duration::from_secs_f64(seconds));
                    Ok(Value::None)
                } else {
                    Ok(Value::None)
                }
            },
            
            _ => {
                if let Some((params, body)) = self.functions.get(name).cloned() {
                    if params.len() != arguments.len() {
                        return Err(MeowLangError::new(
                            ErrorCatalog::get("E601"),
                            self.filename.clone(),
                            position.line,
                            position.column,
                        )
                        .with_extra("expected".to_string(), params.len().to_string())
                        .with_extra("received".to_string(), arguments.len().to_string())
                        .with_context(&self.source_lines));
                    }
                    
                    let old_vars = self.variables.clone();
                    
                    for (param, arg) in params.iter().zip(arguments.iter()) {
                        let val = self.execute(arg)?;
                        self.variables.insert(param.clone(), val);
                    }
                    
                    let mut result = Value::None;
                    for stmt in &body {
                        result = self.execute(stmt)?;
                    }
                    
                    self.variables = old_vars;
                    Ok(result)
                } else {
                    Err(MeowLangError::new(
                        ErrorCatalog::get("E600"),
                        self.filename.clone(),
                        position.line,
                        position.column,
                    )
                    .with_extra("func_name".to_string(), name.to_string())
                    .with_context(&self.source_lines))
                }
            }
        }
    }
}
