use crate::token::{Token, TokenType, TokenValue};
use crate::error::{ErrorCatalog, MeowLangError};

pub struct Lexer {
    chars: Vec<char>,
    filename: String,
    lines: Vec<String>,
    pos: usize,
    line: usize,
    column: usize,
    tokens: Vec<Token>,
    indent_stack: Vec<usize>,
    at_line_start: bool,
}

impl Lexer {
    pub fn new(source: String, filename: String) -> Self {
        let lines: Vec<String> = source.lines().map(|s| s.to_string()).collect();
        let chars: Vec<char> = source.chars().collect();
        
        Lexer {
            chars,
            filename,
            lines,
            pos: 0,
            line: 1,
            column: 1,
            tokens: Vec::new(),
            indent_stack: vec![0],
            at_line_start: true,
        }
    }
    
    fn current_char(&self) -> Option<char> {
        if self.pos < self.chars.len() {
            Some(self.chars[self.pos])
        } else {
            None
        }
    }
    
    fn peek_char(&self, offset: usize) -> Option<char> {
        if self.pos + offset < self.chars.len() {
            Some(self.chars[self.pos + offset])
        } else {
            None
        }
    }
    
    fn advance(&mut self) {
        if let Some(ch) = self.current_char() {
            if ch == '\n' {
                self.line += 1;
                self.column = 1;
                self.at_line_start = true;
            } else {
                self.column += 1;
            }
            self.pos += 1;
        }
    }
    
    fn skip_whitespace(&mut self, skip_newlines: bool) {
        while let Some(ch) = self.current_char() {
            if ch == ' ' || ch == '\t' || ch == '\r' {
                self.advance();
            } else if skip_newlines && ch == '\n' {
                self.advance();
            } else {
                break;
            }
        }
    }
    
    fn skip_comment(&mut self) {
        if self.current_char() == Some('#') {
            while self.current_char().is_some() && self.current_char() != Some('\n') {
                self.advance();
            }
        }
    }
    
    fn read_string(&mut self) -> Result<String, MeowLangError> {
        let start_line = self.line;
        let start_column = self.column;
        let quote_char = self.current_char().unwrap();
        self.advance();
        
        let mut result = String::new();
        
        while self.current_char().is_some() && self.current_char() != Some(quote_char) {
            if self.current_char() == Some('\\') {
                self.advance();
                if let Some(ch) = self.current_char() {
                    let escaped = match ch {
                        'n' => '\n',
                        't' => '\t',
                        'r' => '\r',
                        '\\' => '\\',
                        '"' => '"',
                        '\'' => '\'',
                        _ => ch,
                    };
                    result.push(escaped);
                    self.advance();
                }
            } else {
                result.push(self.current_char().unwrap());
                self.advance();
            }
        }
        
        if self.current_char().is_none() {
            return Err(MeowLangError::new(
                ErrorCatalog::get("E101"),
                self.filename.clone(),
                start_line,
                start_column,
            ).with_context(&self.lines));
        }
        
        self.advance();
        Ok(result)
    }
    
    fn read_number(&mut self) -> (f64, bool) {
        let start = self.pos;
        let mut has_dot = false;
        
        while let Some(ch) = self.current_char() {
            if ch.is_ascii_digit() {
                self.advance();
            } else if ch == '.' && !has_dot {
                if let Some(next) = self.peek_char(1) {
                    if next.is_ascii_digit() {
                        has_dot = true;
                        self.advance();
                    } else {
                        break;
                    }
                } else {
                    break;
                }
            } else {
                break;
            }
        }
        
        let number_str: String = self.chars[start..self.pos].iter().collect();
        let number = number_str.parse::<f64>().unwrap_or(0.0);
        (number, has_dot)
    }
    
    fn read_identifier(&mut self) -> String {
        let start = self.pos;
        
        while let Some(ch) = self.current_char() {
            if ch.is_alphanumeric() || ch == '_' {
                self.advance();
            } else {
                break;
            }
        }
        
        self.chars[start..self.pos].iter().collect()
    }
    
    fn get_keyword_token(&mut self, identifier: &str, line: usize, column: usize) -> Token {
        let lower = identifier.to_lowercase();
        
        match lower.as_str() {
            "miaou" => Token::simple(TokenType::Miaou, line, column),
            "meow" => Token::simple(TokenType::Meow, line, column),
            "ecrire" => Token::simple(TokenType::Ecrire, line, column),
            "demander" => Token::simple(TokenType::Demander, line, column),
            "si" => Token::simple(TokenType::Si, line, column),
            "alors" => Token::simple(TokenType::Alors, line, column),
            "sinon" => {
                self.skip_whitespace(false);
                if let Some(ch) = self.current_char() {
                    if ch == 's' {
                        let next_word = self.peek_identifier();
                        if next_word.to_lowercase() == "si" {
                            self.read_identifier();
                            return Token::simple(TokenType::SinonSi, line, column);
                        }
                    }
                }
                Token::simple(TokenType::Sinon, line, column)
            },
            "repeter" => Token::simple(TokenType::Repeter, line, column),
            "fois" => Token::simple(TokenType::Fois, line, column),
            "tant" => {
                self.skip_whitespace(false);
                if let Some(ch) = self.current_char() {
                    if ch == 'q' {
                        let next_word = self.peek_identifier();
                        if next_word.to_lowercase() == "que" {
                            self.read_identifier();
                            return Token::simple(TokenType::TantQue, line, column);
                        }
                    }
                }
                Token::new(TokenType::Identifier, TokenValue::String(identifier.to_string()), line, column)
            },
            "pour" => {
                self.skip_whitespace(false);
                if let Some(ch) = self.current_char() {
                    if ch == 'c' {
                        let next_word = self.peek_identifier();
                        if next_word.to_lowercase() == "chaque" {
                            self.read_identifier();
                            return Token::simple(TokenType::PourChaque, line, column);
                        }
                    }
                }
                Token::new(TokenType::Identifier, TokenValue::String(identifier.to_string()), line, column)
            },
            "dans" => Token::simple(TokenType::Dans, line, column),
            "compteur" => Token::simple(TokenType::Compteur, line, column),
            "fonction" => Token::simple(TokenType::Fonction, line, column),
            "retour" => Token::simple(TokenType::Retour, line, column),
            "liste" => Token::simple(TokenType::Liste, line, column),
            "dictionnaire" => Token::simple(TokenType::Dictionnaire, line, column),
            "essayer" => Token::simple(TokenType::Essayer, line, column),
            "sauf" => Token::simple(TokenType::Sauf, line, column),
            "erreur" => Token::simple(TokenType::Erreur, line, column),
            "importer" => Token::simple(TokenType::Importer, line, column),
            "minuscule" => Token::simple(TokenType::Minuscule, line, column),
            "majuscule" => Token::simple(TokenType::Majuscule, line, column),
            "longueur" => Token::simple(TokenType::Longueur, line, column),
            "remplacer" => Token::simple(TokenType::Remplacer, line, column),
            "contient" => Token::simple(TokenType::Contient, line, column),
            "aleatoire" => Token::simple(TokenType::Aleatoire, line, column),
            "sqrt" => Token::simple(TokenType::Sqrt, line, column),
            "abs" => Token::simple(TokenType::Abs, line, column),
            "round" => Token::simple(TokenType::Round, line, column),
            "floor" => Token::simple(TokenType::Floor, line, column),
            "ceil" => Token::simple(TokenType::Ceil, line, column),
            "ouvrir" => Token::simple(TokenType::Ouvrir, line, column),
            "lire" => Token::simple(TokenType::Lire, line, column),
            "fermer" => Token::simple(TokenType::Fermer, line, column),
            "attendre" => Token::simple(TokenType::Attendre, line, column),
            "vrai" => Token::new(TokenType::Boolean, TokenValue::Boolean(true), line, column),
            "faux" => Token::new(TokenType::Boolean, TokenValue::Boolean(false), line, column),
            "et" => Token::simple(TokenType::Et, line, column),
            "ou" => Token::simple(TokenType::Ou, line, column),
            "non" => Token::simple(TokenType::Non, line, column),
            "a" => Token::simple(TokenType::A, line, column),
            _ => Token::new(TokenType::Identifier, TokenValue::String(identifier.to_string()), line, column),
        }
    }
    
    fn peek_identifier(&self) -> String {
        let mut pos = self.pos;
        let mut result = String::new();
        
        while pos < self.chars.len() {
            let ch = self.chars[pos];
            if ch.is_alphanumeric() || ch == '_' {
                result.push(ch);
                pos += 1;
            } else {
                break;
            }
        }
        
        result
    }
    
    fn handle_indentation(&mut self, indent_level: usize) {
        let current_indent = *self.indent_stack.last().unwrap();
        
        if indent_level > current_indent {
            self.indent_stack.push(indent_level);
            self.tokens.push(Token::new(
                TokenType::Indent,
                TokenValue::Indent(indent_level),
                self.line,
                1,
            ));
        } else if indent_level < current_indent {
            while !self.indent_stack.is_empty() && *self.indent_stack.last().unwrap() > indent_level {
                self.indent_stack.pop();
                self.tokens.push(Token::new(
                    TokenType::Dedent,
                    TokenValue::Indent(indent_level),
                    self.line,
                    1,
                ));
            }
        }
    }
    
    pub fn tokenize(&mut self) -> Result<Vec<Token>, MeowLangError> {
        while self.pos < self.chars.len() {
            if self.at_line_start {
                let mut indent_level = 0;
                
                while let Some(ch) = self.current_char() {
                    if ch == ' ' {
                        indent_level += 1;
                        self.advance();
                    } else if ch == '\t' {
                        indent_level += 4;
                        self.advance();
                    } else {
                        break;
                    }
                }
                
                if self.current_char() == Some('#') {
                    self.skip_comment();
                    continue;
                }
                
                if self.current_char() == Some('\n') {
                    self.advance();
                    continue;
                }
                
                if self.current_char().is_none() {
                    break;
                }
                
                self.handle_indentation(indent_level);
                self.at_line_start = false;
                continue;
            }
            
            let ch = match self.current_char() {
                Some(c) => c,
                None => break,
            };
            
            if ch == ' ' || ch == '\t' || ch == '\r' {
                self.skip_whitespace(false);
                continue;
            }
            
            if ch == '#' {
                self.skip_comment();
                continue;
            }
            
            if ch == '\n' {
                self.tokens.push(Token::simple(TokenType::Newline, self.line, self.column));
                self.advance();
                continue;
            }
            
            if ch == '"' || ch == '\'' {
                let line = self.line;
                let column = self.column;
                let string_val = self.read_string()?;
                self.tokens.push(Token::new(
                    TokenType::String,
                    TokenValue::String(string_val),
                    line,
                    column,
                ));
                continue;
            }
            
            if ch.is_ascii_digit() {
                let line = self.line;
                let column = self.column;
                let (number, has_dot) = self.read_number();
                
                if has_dot {
                    self.tokens.push(Token::new(TokenType::Number, TokenValue::Number(number), line, column));
                } else {
                    self.tokens.push(Token::new(TokenType::Number, TokenValue::Integer(number as i64), line, column));
                }
                continue;
            }
            
            if ch.is_alphabetic() || ch == '_' {
                let line = self.line;
                let column = self.column;
                let identifier = self.read_identifier();
                let token = self.get_keyword_token(&identifier, line, column);
                self.tokens.push(token);
                continue;
            }
            
            let line = self.line;
            let column = self.column;
            
            match ch {
                '+' => {
                    self.advance();
                    self.tokens.push(Token::simple(TokenType::Plus, line, column));
                },
                '-' => {
                    self.advance();
                    self.tokens.push(Token::simple(TokenType::Minus, line, column));
                },
                '*' => {
                    self.advance();
                    if self.current_char() == Some('*') {
                        self.advance();
                        self.tokens.push(Token::simple(TokenType::Power, line, column));
                    } else {
                        self.tokens.push(Token::simple(TokenType::Multiply, line, column));
                    }
                },
                '/' => {
                    self.advance();
                    if self.current_char() == Some('/') {
                        self.advance();
                        self.tokens.push(Token::simple(TokenType::FloorDiv, line, column));
                    } else {
                        self.tokens.push(Token::simple(TokenType::Divide, line, column));
                    }
                },
                '%' => {
                    self.advance();
                    self.tokens.push(Token::simple(TokenType::Modulo, line, column));
                },
                '=' => {
                    self.advance();
                    if self.current_char() == Some('=') {
                        self.advance();
                        self.tokens.push(Token::simple(TokenType::Equal, line, column));
                    } else {
                        self.tokens.push(Token::simple(TokenType::Assign, line, column));
                    }
                },
                '!' => {
                    self.advance();
                    if self.current_char() == Some('=') {
                        self.advance();
                        self.tokens.push(Token::simple(TokenType::NotEqual, line, column));
                    }
                },
                '<' => {
                    self.advance();
                    if self.current_char() == Some('=') {
                        self.advance();
                        self.tokens.push(Token::simple(TokenType::LessEqual, line, column));
                    } else {
                        self.tokens.push(Token::simple(TokenType::LessThan, line, column));
                    }
                },
                '>' => {
                    self.advance();
                    if self.current_char() == Some('=') {
                        self.advance();
                        self.tokens.push(Token::simple(TokenType::GreaterEqual, line, column));
                    } else {
                        self.tokens.push(Token::simple(TokenType::GreaterThan, line, column));
                    }
                },
                ':' => {
                    self.advance();
                    self.tokens.push(Token::simple(TokenType::Colon, line, column));
                },
                ',' => {
                    self.advance();
                    self.tokens.push(Token::simple(TokenType::Comma, line, column));
                },
                '(' => {
                    self.advance();
                    self.tokens.push(Token::simple(TokenType::LParen, line, column));
                },
                ')' => {
                    self.advance();
                    self.tokens.push(Token::simple(TokenType::RParen, line, column));
                },
                '[' => {
                    self.advance();
                    self.tokens.push(Token::simple(TokenType::LBracket, line, column));
                },
                ']' => {
                    self.advance();
                    self.tokens.push(Token::simple(TokenType::RBracket, line, column));
                },
                '.' => {
                    self.advance();
                    self.tokens.push(Token::simple(TokenType::Dot, line, column));
                },
                _ => {
                    return Err(MeowLangError::new(
                        ErrorCatalog::get("E100"),
                        self.filename.clone(),
                        line,
                        column,
                    ).with_instruction(ch.to_string()).with_context(&self.lines));
                }
            }
        }
        
        while self.indent_stack.len() > 1 {
            self.indent_stack.pop();
            self.tokens.push(Token::simple(TokenType::Dedent, self.line, self.column));
        }
        
        self.tokens.push(Token::simple(TokenType::Eof, self.line, self.column));
        
        Ok(self.tokens.clone())
    }
}
