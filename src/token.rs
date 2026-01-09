use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub enum TokenType {
    Miaou,
    Meow,
    
    Ecrire,
    Demander,
    Texte,
    Nombre,
    
    Si,
    Alors,
    Sinon,
    SinonSi,
    
    Repeter,
    Fois,
    TantQue,
    PourChaque,
    Dans,
    Compteur,
    
    Fonction,
    Retour,
    
    Liste,
    Dictionnaire,
    
    Essayer,
    Sauf,
    Erreur,
    
    Importer,
    
    Minuscule,
    Majuscule,
    Longueur,
    Remplacer,
    Contient,
    
    Aleatoire,
    Sqrt,
    Abs,
    Round,
    Floor,
    Ceil,
    
    Ouvrir,
    Lire,
    Fermer,
    
    Attendre,
    
    Identifier,
    String,
    Number,
    Boolean,
    
    Plus,
    Minus,
    Multiply,
    Divide,
    FloorDiv,
    Modulo,
    Power,
    
    Assign,
    Equal,
    NotEqual,
    LessThan,
    GreaterThan,
    LessEqual,
    GreaterEqual,
    
    Et,
    Ou,
    Non,
    
    A,
    
    Colon,
    Comma,
    LParen,
    RParen,
    LBracket,
    RBracket,
    Dot,
    
    Newline,
    Indent,
    Dedent,
    
    Comment,
    Eof,
}

impl fmt::Display for TokenType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}", self)
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum TokenValue {
    None,
    String(String),
    Number(f64),
    Integer(i64),
    Boolean(bool),
    Indent(usize),
}

#[derive(Debug, Clone, PartialEq)]
pub struct Token {
    pub token_type: TokenType,
    pub value: TokenValue,
    pub line: usize,
    pub column: usize,
}

impl Token {
    pub fn new(token_type: TokenType, value: TokenValue, line: usize, column: usize) -> Self {
        Token {
            token_type,
            value,
            line,
            column,
        }
    }
    
    pub fn simple(token_type: TokenType, line: usize, column: usize) -> Self {
        Token::new(token_type, TokenValue::None, line, column)
    }
}

impl fmt::Display for Token {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Token({:?}, {:?}, {}:{})", self.token_type, self.value, self.line, self.column)
    }
}
