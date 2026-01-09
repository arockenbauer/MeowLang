use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub struct Position {
    pub line: usize,
    pub column: usize,
}

impl Position {
    pub fn new(line: usize, column: usize) -> Self {
        Position { line, column }
    }
}

impl fmt::Display for Position {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}:{}", self.line, self.column)
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum ASTNode {
    Program {
        statements: Vec<ASTNode>,
        position: Position,
    },
    
    Literal {
        value: LiteralValue,
        position: Position,
    },
    
    Identifier {
        name: String,
        position: Position,
    },
    
    BinaryOp {
        left: Box<ASTNode>,
        operator: String,
        right: Box<ASTNode>,
        position: Position,
    },
    
    UnaryOp {
        operator: String,
        operand: Box<ASTNode>,
        position: Position,
    },
    
    Assignment {
        name: String,
        value: Box<ASTNode>,
        position: Position,
    },
    
    FunctionCall {
        name: String,
        arguments: Vec<ASTNode>,
        position: Position,
    },
    
    IfStatement {
        condition: Box<ASTNode>,
        then_block: Vec<ASTNode>,
        elif_blocks: Vec<(ASTNode, Vec<ASTNode>)>,
        else_block: Option<Vec<ASTNode>>,
        position: Position,
    },
    
    WhileLoop {
        condition: Box<ASTNode>,
        body: Vec<ASTNode>,
        position: Position,
    },
    
    RepeatLoop {
        count: Box<ASTNode>,
        body: Vec<ASTNode>,
        position: Position,
    },
    
    ForEachLoop {
        iterator: String,
        iterable: Box<ASTNode>,
        body: Vec<ASTNode>,
        position: Position,
    },
    
    FunctionDef {
        name: String,
        parameters: Vec<String>,
        body: Vec<ASTNode>,
        position: Position,
    },
    
    ReturnStatement {
        value: Option<Box<ASTNode>>,
        position: Position,
    },
    
    ListNode {
        elements: Vec<ASTNode>,
        position: Position,
    },
    
    DictNode {
        pairs: Vec<(ASTNode, ASTNode)>,
        position: Position,
    },
    
    IndexAccess {
        object: Box<ASTNode>,
        index: Box<ASTNode>,
        position: Position,
    },
    
    IndexAssignment {
        object: Box<ASTNode>,
        index: Box<ASTNode>,
        value: Box<ASTNode>,
        position: Position,
    },
    
    TryExcept {
        try_block: Vec<ASTNode>,
        except_block: Vec<ASTNode>,
        position: Position,
    },
    
    ExpressionStatement {
        expression: Box<ASTNode>,
        position: Position,
    },
}

#[derive(Debug, Clone, PartialEq)]
pub enum LiteralValue {
    String(String),
    Number(f64),
    Integer(i64),
    Boolean(bool),
    None,
}

impl ASTNode {
    pub fn position(&self) -> &Position {
        match self {
            ASTNode::Program { position, .. } => position,
            ASTNode::Literal { position, .. } => position,
            ASTNode::Identifier { position, .. } => position,
            ASTNode::BinaryOp { position, .. } => position,
            ASTNode::UnaryOp { position, .. } => position,
            ASTNode::Assignment { position, .. } => position,
            ASTNode::FunctionCall { position, .. } => position,
            ASTNode::IfStatement { position, .. } => position,
            ASTNode::WhileLoop { position, .. } => position,
            ASTNode::RepeatLoop { position, .. } => position,
            ASTNode::ForEachLoop { position, .. } => position,
            ASTNode::FunctionDef { position, .. } => position,
            ASTNode::ReturnStatement { position, .. } => position,
            ASTNode::ListNode { position, .. } => position,
            ASTNode::DictNode { position, .. } => position,
            ASTNode::IndexAccess { position, .. } => position,
            ASTNode::IndexAssignment { position, .. } => position,
            ASTNode::TryExcept { position, .. } => position,
            ASTNode::ExpressionStatement { position, .. } => position,
        }
    }
}
