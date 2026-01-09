pub mod token;
pub mod error;
pub mod lexer;
pub mod ast;
pub mod parser;
pub mod interpreter;

use std::fs;
use lexer::Lexer;
use parser::Parser;
use interpreter::Interpreter;
use error::MeowLangError;

pub fn run_file(filename: &str) -> Result<(), MeowLangError> {
    let source = fs::read_to_string(filename).map_err(|_| {
        MeowLangError::new(
            error::ErrorCatalog::get("E900"),
            filename.to_string(),
            1,
            1,
        )
        .with_extra("filename".to_string(), filename.to_string())
    })?;
    
    run(source, filename.to_string())
}

pub fn run(source: String, filename: String) -> Result<(), MeowLangError> {
    let source_lines: Vec<String> = source.lines().map(|s| s.to_string()).collect();
    
    let mut lexer = Lexer::new(source.clone(), filename.clone());
    let tokens = lexer.tokenize()?;
    
    let mut parser = Parser::new(tokens, filename.clone(), source_lines.clone());
    let ast = parser.parse()?;
    
    let mut interpreter = Interpreter::new(filename, source_lines);
    interpreter.execute(&ast)?;
    
    Ok(())
}
