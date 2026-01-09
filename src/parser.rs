use crate::ast::{ASTNode, LiteralValue, Position};
use crate::token::{Token, TokenType, TokenValue};
use crate::error::{ErrorCatalog, MeowLangError};

pub struct Parser {
    tokens: Vec<Token>,
    pos: usize,
    filename: String,
    source_lines: Vec<String>,
}

impl Parser {
    pub fn new(tokens: Vec<Token>, filename: String, source_lines: Vec<String>) -> Self {
        Parser {
            tokens,
            pos: 0,
            filename,
            source_lines,
        }
    }
    
    fn current(&self) -> &Token {
        if self.pos < self.tokens.len() {
            &self.tokens[self.pos]
        } else {
            self.tokens.last().unwrap()
        }
    }
    
    fn peek(&self, offset: usize) -> Option<&Token> {
        self.tokens.get(self.pos + offset)
    }
    
    fn advance(&mut self) {
        if self.pos < self.tokens.len() {
            self.pos += 1;
        }
    }
    
    fn expect(&mut self, token_type: TokenType) -> Result<Token, MeowLangError> {
        if self.current().token_type == token_type {
            let token = self.current().clone();
            self.advance();
            Ok(token)
        } else {
            Err(MeowLangError::new(
                ErrorCatalog::get("E104"),
                self.filename.clone(),
                self.current().line,
                self.current().column,
            ).with_context(&self.source_lines))
        }
    }
    
    fn skip_newlines(&mut self) {
        while self.current().token_type == TokenType::Newline {
            self.advance();
        }
    }
    
    fn position_from_token(&self, token: &Token) -> Position {
        Position::new(token.line, token.column)
    }
    
    pub fn parse(&mut self) -> Result<ASTNode, MeowLangError> {
        self.skip_newlines();
        
        if self.current().token_type != TokenType::Miaou {
            return Err(MeowLangError::new(
                ErrorCatalog::get("E000"),
                self.filename.clone(),
                1,
                1,
            ).with_context(&self.source_lines));
        }
        
        let start_pos = self.position_from_token(self.current());
        self.advance();
        self.skip_newlines();
        
        let mut statements = Vec::new();
        
        while self.current().token_type != TokenType::Meow && self.current().token_type != TokenType::Eof {
            statements.push(self.parse_statement()?);
            self.skip_newlines();
        }
        
        if self.current().token_type != TokenType::Meow {
            return Err(MeowLangError::new(
                ErrorCatalog::get("E001"),
                self.filename.clone(),
                self.current().line,
                self.current().column,
            ).with_context(&self.source_lines));
        }
        
        Ok(ASTNode::Program {
            statements,
            position: start_pos,
        })
    }
    
    fn parse_statement(&mut self) -> Result<ASTNode, MeowLangError> {
        self.skip_newlines();
        
        match self.current().token_type {
            TokenType::Ecrire => self.parse_ecrire(),
            TokenType::Si => self.parse_if(),
            TokenType::Repeter => self.parse_repeat(),
            TokenType::TantQue => self.parse_while(),
            TokenType::PourChaque => self.parse_foreach(),
            TokenType::Fonction => self.parse_function_def(),
            TokenType::Retour => self.parse_return(),
            TokenType::Essayer => self.parse_try_except(),
            TokenType::Identifier => {
                if self.peek(1).map(|t| &t.token_type) == Some(&TokenType::Assign) {
                    self.parse_assignment()
                } else if self.peek(1).map(|t| &t.token_type) == Some(&TokenType::LParen) {
                    let expr = self.parse_expression()?;
                    self.skip_newlines();
                    Ok(ASTNode::ExpressionStatement {
                        expression: Box::new(expr.clone()),
                        position: expr.position().clone(),
                    })
                } else {
                    let expr = self.parse_expression()?;
                    self.skip_newlines();
                    Ok(ASTNode::ExpressionStatement {
                        expression: Box::new(expr.clone()),
                        position: expr.position().clone(),
                    })
                }
            },
            _ => {
                let expr = self.parse_expression()?;
                self.skip_newlines();
                Ok(ASTNode::ExpressionStatement {
                    expression: Box::new(expr.clone()),
                    position: expr.position().clone(),
                })
            }
        }
    }
    
    fn parse_ecrire(&mut self) -> Result<ASTNode, MeowLangError> {
        let token = self.current().clone();
        let position = self.position_from_token(&token);
        self.advance();
        
        let mut args = Vec::new();
        
        loop {
            self.skip_newlines();
            if self.current().token_type == TokenType::Newline || 
               self.current().token_type == TokenType::Eof {
                break;
            }
            
            args.push(self.parse_expression()?);
            
            if self.current().token_type != TokenType::Newline &&
               self.current().token_type != TokenType::Eof &&
               self.current().token_type != TokenType::Comma {
                continue;
            }
            
            if self.current().token_type == TokenType::Comma {
                self.advance();
            } else {
                break;
            }
        }
        
        Ok(ASTNode::FunctionCall {
            name: "ecrire".to_string(),
            arguments: args,
            position,
        })
    }
    
    fn parse_assignment(&mut self) -> Result<ASTNode, MeowLangError> {
        let name_token = self.current().clone();
        let position = self.position_from_token(&name_token);
        
        let name = if let TokenValue::String(s) = &name_token.value {
            s.clone()
        } else {
            return Err(MeowLangError::new(
                ErrorCatalog::get("E104"),
                self.filename.clone(),
                name_token.line,
                name_token.column,
            ).with_context(&self.source_lines));
        };
        
        self.advance();
        self.expect(TokenType::Assign)?;
        
        let value = self.parse_expression()?;
        
        Ok(ASTNode::Assignment {
            name,
            value: Box::new(value),
            position,
        })
    }
    
    fn parse_if(&mut self) -> Result<ASTNode, MeowLangError> {
        let position = self.position_from_token(self.current());
        self.advance();
        
        let condition = self.parse_expression()?;
        
        self.expect(TokenType::Alors)?;
        self.expect(TokenType::Colon)?;
        self.skip_newlines();
        self.expect(TokenType::Indent)?;
        
        let then_block = self.parse_block()?;
        
        let mut elif_blocks = Vec::new();
        let mut else_block = None;
        
        self.skip_newlines();
        
        while self.current().token_type == TokenType::SinonSi {
            self.advance();
            let elif_condition = self.parse_expression()?;
            self.expect(TokenType::Alors)?;
            self.expect(TokenType::Colon)?;
            self.skip_newlines();
            self.expect(TokenType::Indent)?;
            let elif_body = self.parse_block()?;
            elif_blocks.push((elif_condition, elif_body));
            self.skip_newlines();
        }
        
        if self.current().token_type == TokenType::Sinon {
            self.advance();
            self.expect(TokenType::Colon)?;
            self.skip_newlines();
            self.expect(TokenType::Indent)?;
            else_block = Some(self.parse_block()?);
        }
        
        Ok(ASTNode::IfStatement {
            condition: Box::new(condition),
            then_block,
            elif_blocks,
            else_block,
            position,
        })
    }
    
    fn parse_while(&mut self) -> Result<ASTNode, MeowLangError> {
        let position = self.position_from_token(self.current());
        self.advance();
        
        let condition = self.parse_expression()?;
        
        self.expect(TokenType::Colon)?;
        self.skip_newlines();
        self.expect(TokenType::Indent)?;
        
        let body = self.parse_block()?;
        
        Ok(ASTNode::WhileLoop {
            condition: Box::new(condition),
            body,
            position,
        })
    }
    
    fn parse_repeat(&mut self) -> Result<ASTNode, MeowLangError> {
        let position = self.position_from_token(self.current());
        self.advance();
        
        let count = self.parse_expression()?;
        
        self.expect(TokenType::Fois)?;
        self.expect(TokenType::Colon)?;
        self.skip_newlines();
        self.expect(TokenType::Indent)?;
        
        let body = self.parse_block()?;
        
        Ok(ASTNode::RepeatLoop {
            count: Box::new(count),
            body,
            position,
        })
    }
    
    fn parse_foreach(&mut self) -> Result<ASTNode, MeowLangError> {
        let position = self.position_from_token(self.current());
        self.advance();
        
        let iterator_token = self.expect(TokenType::Identifier)?;
        let iterator = if let TokenValue::String(s) = iterator_token.value {
            s
        } else {
            return Err(MeowLangError::new(
                ErrorCatalog::get("E104"),
                self.filename.clone(),
                iterator_token.line,
                iterator_token.column,
            ).with_context(&self.source_lines));
        };
        
        self.expect(TokenType::Dans)?;
        
        let iterable = self.parse_expression()?;
        
        self.expect(TokenType::Colon)?;
        self.skip_newlines();
        self.expect(TokenType::Indent)?;
        
        let body = self.parse_block()?;
        
        Ok(ASTNode::ForEachLoop {
            iterator,
            iterable: Box::new(iterable),
            body,
            position,
        })
    }
    
    fn parse_function_def(&mut self) -> Result<ASTNode, MeowLangError> {
        let position = self.position_from_token(self.current());
        self.advance();
        
        let name_token = self.expect(TokenType::Identifier)?;
        let name = if let TokenValue::String(s) = name_token.value {
            s
        } else {
            return Err(MeowLangError::new(
                ErrorCatalog::get("E104"),
                self.filename.clone(),
                name_token.line,
                name_token.column,
            ).with_context(&self.source_lines));
        };
        
        self.expect(TokenType::LParen)?;
        
        let mut parameters = Vec::new();
        
        while self.current().token_type != TokenType::RParen {
            let param_token = self.expect(TokenType::Identifier)?;
            if let TokenValue::String(s) = param_token.value {
                parameters.push(s);
            }
            
            if self.current().token_type == TokenType::Comma {
                self.advance();
            }
        }
        
        self.expect(TokenType::RParen)?;
        self.expect(TokenType::Colon)?;
        self.skip_newlines();
        self.expect(TokenType::Indent)?;
        
        let body = self.parse_block()?;
        
        Ok(ASTNode::FunctionDef {
            name,
            parameters,
            body,
            position,
        })
    }
    
    fn parse_return(&mut self) -> Result<ASTNode, MeowLangError> {
        let position = self.position_from_token(self.current());
        self.advance();
        
        if self.current().token_type == TokenType::Newline || 
           self.current().token_type == TokenType::Eof {
            return Ok(ASTNode::ReturnStatement {
                value: None,
                position,
            });
        }
        
        let value = self.parse_expression()?;
        
        Ok(ASTNode::ReturnStatement {
            value: Some(Box::new(value)),
            position,
        })
    }
    
    fn parse_try_except(&mut self) -> Result<ASTNode, MeowLangError> {
        let position = self.position_from_token(self.current());
        self.advance();
        
        self.expect(TokenType::Colon)?;
        self.skip_newlines();
        self.expect(TokenType::Indent)?;
        
        let try_block = self.parse_block()?;
        
        self.skip_newlines();
        self.expect(TokenType::Sauf)?;
        self.expect(TokenType::Erreur)?;
        self.expect(TokenType::Colon)?;
        self.skip_newlines();
        self.expect(TokenType::Indent)?;
        
        let except_block = self.parse_block()?;
        
        Ok(ASTNode::TryExcept {
            try_block,
            except_block,
            position,
        })
    }
    
    fn parse_block(&mut self) -> Result<Vec<ASTNode>, MeowLangError> {
        let mut statements = Vec::new();
        
        self.skip_newlines();
        
        while self.current().token_type != TokenType::Dedent && 
              self.current().token_type != TokenType::Eof {
            statements.push(self.parse_statement()?);
            self.skip_newlines();
        }
        
        if self.current().token_type == TokenType::Dedent {
            self.advance();
        }
        
        Ok(statements)
    }
    
    fn parse_expression(&mut self) -> Result<ASTNode, MeowLangError> {
        self.parse_or()
    }
    
    fn parse_or(&mut self) -> Result<ASTNode, MeowLangError> {
        let mut left = self.parse_and()?;
        
        while self.current().token_type == TokenType::Ou {
            let position = self.position_from_token(self.current());
            self.advance();
            let right = self.parse_and()?;
            left = ASTNode::BinaryOp {
                left: Box::new(left),
                operator: "ou".to_string(),
                right: Box::new(right),
                position,
            };
        }
        
        Ok(left)
    }
    
    fn parse_and(&mut self) -> Result<ASTNode, MeowLangError> {
        let mut left = self.parse_not()?;
        
        while self.current().token_type == TokenType::Et {
            let position = self.position_from_token(self.current());
            self.advance();
            let right = self.parse_not()?;
            left = ASTNode::BinaryOp {
                left: Box::new(left),
                operator: "et".to_string(),
                right: Box::new(right),
                position,
            };
        }
        
        Ok(left)
    }
    
    fn parse_not(&mut self) -> Result<ASTNode, MeowLangError> {
        if self.current().token_type == TokenType::Non {
            let position = self.position_from_token(self.current());
            self.advance();
            let operand = self.parse_not()?;
            return Ok(ASTNode::UnaryOp {
                operator: "non".to_string(),
                operand: Box::new(operand),
                position,
            });
        }
        
        self.parse_comparison()
    }
    
    fn parse_comparison(&mut self) -> Result<ASTNode, MeowLangError> {
        let mut left = self.parse_additive()?;
        
        while matches!(
            self.current().token_type,
            TokenType::Assign
                | TokenType::Equal
                | TokenType::NotEqual
                | TokenType::LessThan
                | TokenType::GreaterThan
                | TokenType::LessEqual
                | TokenType::GreaterEqual
        ) {
            let position = self.position_from_token(self.current());
            let operator = match self.current().token_type {
                TokenType::Assign => "=",
                TokenType::Equal => "=",
                TokenType::NotEqual => "!=",
                TokenType::LessThan => "<",
                TokenType::GreaterThan => ">",
                TokenType::LessEqual => "<=",
                TokenType::GreaterEqual => ">=",
                _ => "",
            };
            self.advance();
            let right = self.parse_additive()?;
            left = ASTNode::BinaryOp {
                left: Box::new(left),
                operator: operator.to_string(),
                right: Box::new(right),
                position,
            };
        }
        
        Ok(left)
    }
    
    fn parse_additive(&mut self) -> Result<ASTNode, MeowLangError> {
        let mut left = self.parse_multiplicative()?;
        
        while self.current().token_type == TokenType::Plus || 
              self.current().token_type == TokenType::Minus {
            let position = self.position_from_token(self.current());
            let operator = if self.current().token_type == TokenType::Plus {
                "+"
            } else {
                "-"
            };
            self.advance();
            let right = self.parse_multiplicative()?;
            left = ASTNode::BinaryOp {
                left: Box::new(left),
                operator: operator.to_string(),
                right: Box::new(right),
                position,
            };
        }
        
        Ok(left)
    }
    
    fn parse_multiplicative(&mut self) -> Result<ASTNode, MeowLangError> {
        let mut left = self.parse_power()?;
        
        while matches!(
            self.current().token_type,
            TokenType::Multiply | TokenType::Divide | TokenType::FloorDiv | TokenType::Modulo
        ) {
            let position = self.position_from_token(self.current());
            let operator = match self.current().token_type {
                TokenType::Multiply => "*",
                TokenType::Divide => "/",
                TokenType::FloorDiv => "//",
                TokenType::Modulo => "%",
                _ => "",
            };
            self.advance();
            let right = self.parse_power()?;
            left = ASTNode::BinaryOp {
                left: Box::new(left),
                operator: operator.to_string(),
                right: Box::new(right),
                position,
            };
        }
        
        Ok(left)
    }
    
    fn parse_power(&mut self) -> Result<ASTNode, MeowLangError> {
        let mut left = self.parse_unary()?;
        
        if self.current().token_type == TokenType::Power {
            let position = self.position_from_token(self.current());
            self.advance();
            let right = self.parse_power()?;
            left = ASTNode::BinaryOp {
                left: Box::new(left),
                operator: "**".to_string(),
                right: Box::new(right),
                position,
            };
        }
        
        Ok(left)
    }
    
    fn parse_unary(&mut self) -> Result<ASTNode, MeowLangError> {
        if self.current().token_type == TokenType::Minus {
            let position = self.position_from_token(self.current());
            self.advance();
            let operand = self.parse_unary()?;
            return Ok(ASTNode::UnaryOp {
                operator: "-".to_string(),
                operand: Box::new(operand),
                position,
            });
        }
        
        self.parse_postfix()
    }
    
    fn parse_postfix(&mut self) -> Result<ASTNode, MeowLangError> {
        let mut expr = self.parse_primary()?;
        
        loop {
            match self.current().token_type {
                TokenType::LParen => {
                    if let ASTNode::Identifier { name, .. } = expr {
                        let position = self.position_from_token(self.current());
                        self.advance();
                        
                        let mut arguments = Vec::new();
                        
                        while self.current().token_type != TokenType::RParen {
                            arguments.push(self.parse_expression()?);
                            
                            if self.current().token_type == TokenType::Comma {
                                self.advance();
                            }
                        }
                        
                        self.expect(TokenType::RParen)?;
                        
                        expr = ASTNode::FunctionCall {
                            name,
                            arguments,
                            position,
                        };
                    } else {
                        break;
                    }
                },
                TokenType::LBracket => {
                    let position = self.position_from_token(self.current());
                    self.advance();
                    let index = self.parse_expression()?;
                    self.expect(TokenType::RBracket)?;
                    
                    expr = ASTNode::IndexAccess {
                        object: Box::new(expr),
                        index: Box::new(index),
                        position,
                    };
                },
                _ => break,
            }
        }
        
        Ok(expr)
    }
    
    fn parse_primary(&mut self) -> Result<ASTNode, MeowLangError> {
        let token = self.current().clone();
        let position = self.position_from_token(&token);
        
        match &token.token_type {
            TokenType::Number => {
                self.advance();
                match &token.value {
                    TokenValue::Number(n) => Ok(ASTNode::Literal {
                        value: LiteralValue::Number(*n),
                        position,
                    }),
                    TokenValue::Integer(i) => Ok(ASTNode::Literal {
                        value: LiteralValue::Integer(*i),
                        position,
                    }),
                    _ => unreachable!(),
                }
            },
            TokenType::String => {
                self.advance();
                if let TokenValue::String(s) = &token.value {
                    Ok(ASTNode::Literal {
                        value: LiteralValue::String(s.clone()),
                        position,
                    })
                } else {
                    unreachable!()
                }
            },
            TokenType::Boolean => {
                self.advance();
                if let TokenValue::Boolean(b) = &token.value {
                    Ok(ASTNode::Literal {
                        value: LiteralValue::Boolean(*b),
                        position,
                    })
                } else {
                    unreachable!()
                }
            },
            TokenType::Identifier => {
                self.advance();
                if let TokenValue::String(s) = &token.value {
                    Ok(ASTNode::Identifier {
                        name: s.clone(),
                        position,
                    })
                } else {
                    unreachable!()
                }
            },
            TokenType::Compteur => {
                self.advance();
                Ok(ASTNode::Identifier {
                    name: "compteur".to_string(),
                    position,
                })
            },
            TokenType::LParen => {
                self.advance();
                let expr = self.parse_expression()?;
                self.expect(TokenType::RParen)?;
                Ok(expr)
            },
            TokenType::Liste => {
                self.advance();
                self.expect(TokenType::LParen)?;
                
                let mut elements = Vec::new();
                
                while self.current().token_type != TokenType::RParen {
                    elements.push(self.parse_expression()?);
                    
                    if self.current().token_type == TokenType::Comma {
                        self.advance();
                    }
                }
                
                self.expect(TokenType::RParen)?;
                
                Ok(ASTNode::ListNode {
                    elements,
                    position,
                })
            },
            TokenType::Demander => {
                self.advance();
                
                let type_token = self.current().clone();
                let input_type = if type_token.token_type == TokenType::Identifier {
                    if let TokenValue::String(s) = &type_token.value {
                        let lower = s.to_lowercase();
                        if lower == "texte" || lower == "nombre" {
                            lower
                        } else {
                            return Err(MeowLangError::new(
                                ErrorCatalog::get("E104"),
                                self.filename.clone(),
                                type_token.line,
                                type_token.column,
                            ).with_context(&self.source_lines));
                        }
                    } else {
                        return Err(MeowLangError::new(
                            ErrorCatalog::get("E104"),
                            self.filename.clone(),
                            type_token.line,
                            type_token.column,
                        ).with_context(&self.source_lines));
                    }
                } else {
                    return Err(MeowLangError::new(
                        ErrorCatalog::get("E104"),
                        self.filename.clone(),
                        type_token.line,
                        type_token.column,
                    ).with_context(&self.source_lines));
                };
                self.advance();
                
                let prompt = self.parse_expression()?;
                
                Ok(ASTNode::FunctionCall {
                    name: format!("demander_{}", input_type),
                    arguments: vec![prompt],
                    position,
                })
            },
            TokenType::Minuscule | TokenType::Majuscule | TokenType::Longueur | 
            TokenType::Aleatoire | TokenType::Sqrt | TokenType::Abs | 
            TokenType::Round | TokenType::Floor | TokenType::Ceil | TokenType::Attendre => {
                let func_name = match token.token_type {
                    TokenType::Minuscule => "minuscule",
                    TokenType::Majuscule => "majuscule",
                    TokenType::Longueur => "longueur",
                    TokenType::Aleatoire => "aleatoire",
                    TokenType::Sqrt => "sqrt",
                    TokenType::Abs => "abs",
                    TokenType::Round => "round",
                    TokenType::Floor => "floor",
                    TokenType::Ceil => "ceil",
                    TokenType::Attendre => "attendre",
                    _ => "",
                };
                
                self.advance();
                
                let mut arguments = Vec::new();
                
                if token.token_type == TokenType::Aleatoire {
                    let start = self.parse_expression()?;
                    self.expect(TokenType::A)?;
                    let end = self.parse_expression()?;
                    arguments.push(start);
                    arguments.push(end);
                } else {
                    arguments.push(self.parse_expression()?);
                }
                
                Ok(ASTNode::FunctionCall {
                    name: func_name.to_string(),
                    arguments,
                    position,
                })
            },
            _ => {
                Err(MeowLangError::new(
                    ErrorCatalog::get("E100"),
                    self.filename.clone(),
                    token.line,
                    token.column,
                ).with_context(&self.source_lines))
            }
        }
    }
}
