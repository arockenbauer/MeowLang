"""
Lexer pour MeowLang - Tokenisation du code source.
"""

import re
from typing import List, Optional, Tuple
from enum import Enum, auto


class TokenType(Enum):
    MIAOU = auto()
    MEOW = auto()
    
    ECRIRE = auto()
    DEMANDER = auto()
    TEXTE = auto()
    NOMBRE = auto()
    
    SI = auto()
    ALORS = auto()
    SINON = auto()
    SINON_SI = auto()
    
    REPETER = auto()
    FOIS = auto()
    TANT_QUE = auto()
    POUR_CHAQUE = auto()
    DANS = auto()
    COMPTEUR = auto()
    
    FONCTION = auto()
    RETOUR = auto()
    
    LISTE = auto()
    DICTIONNAIRE = auto()
    
    ESSAYER = auto()
    SAUF = auto()
    ERREUR = auto()
    
    IMPORTER = auto()
    
    MINUSCULE = auto()
    MAJUSCULE = auto()
    LONGUEUR = auto()
    REMPLACER = auto()
    CONTIENT = auto()
    
    ALEATOIRE = auto()
    SQRT = auto()
    ABS = auto()
    ROUND = auto()
    FLOOR = auto()
    CEIL = auto()
    
    OUVRIR = auto()
    LIRE = auto()
    FERMER = auto()
    
    ATTENDRE = auto()
    
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    FLOOR_DIV = auto()
    MODULO = auto()
    POWER = auto()
    
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    
    ET = auto()
    OU = auto()
    NON = auto()
    
    A = auto()
    
    COLON = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    DOT = auto()
    
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    
    COMMENT = auto()
    EOF = auto()


class Token:
    def __init__(self, type_: TokenType, value: any, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"
    
    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (self.type == other.type and 
                self.value == other.value and 
                self.line == other.line and 
                self.column == other.column)


KEYWORDS = {
    'miaou': TokenType.MIAOU,
    'meow': TokenType.MEOW,
    'ecrire': TokenType.ECRIRE,
    'demander': TokenType.DEMANDER,
    'si': TokenType.SI,
    'alors': TokenType.ALORS,
    'sinon': TokenType.SINON,
    'repeter': TokenType.REPETER,
    'fois': TokenType.FOIS,
    'tant': TokenType.TANT_QUE,
    'que': TokenType.TANT_QUE,
    'pour': TokenType.POUR_CHAQUE,
    'chaque': TokenType.POUR_CHAQUE,
    'dans': TokenType.DANS,
    'compteur': TokenType.COMPTEUR,
    'fonction': TokenType.FONCTION,
    'retour': TokenType.RETOUR,
    'liste': TokenType.LISTE,
    'dictionnaire': TokenType.DICTIONNAIRE,
    'essayer': TokenType.ESSAYER,
    'sauf': TokenType.SAUF,
    'erreur': TokenType.ERREUR,
    'importer': TokenType.IMPORTER,
    'minuscule': TokenType.MINUSCULE,
    'majuscule': TokenType.MAJUSCULE,
    'longueur': TokenType.LONGUEUR,
    'remplacer': TokenType.REMPLACER,
    'contient': TokenType.CONTIENT,
    'aleatoire': TokenType.ALEATOIRE,
    'sqrt': TokenType.SQRT,
    'abs': TokenType.ABS,
    'round': TokenType.ROUND,
    'floor': TokenType.FLOOR,
    'ceil': TokenType.CEIL,
    'ouvrir': TokenType.OUVRIR,
    'lire': TokenType.LIRE,
    'fermer': TokenType.FERMER,
    'attendre': TokenType.ATTENDRE,
    'vrai': TokenType.BOOLEAN,
    'faux': TokenType.BOOLEAN,
    'et': TokenType.ET,
    'ou': TokenType.OU,
    'non': TokenType.NON,
}


class Lexer:
    def __init__(self, source: str, filename: str = "<script>"):
        self.source = source
        self.filename = filename
        self.lines = source.split('\n')
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.indent_stack = [0]
        self.at_line_start = True
    
    def error(self, message: str, code: str = "E100"):
        from .errors import ErrorCatalog
        ErrorCatalog.raise_error(
            code=code,
            file=self.filename,
            line=self.line,
            column=self.column,
            instruction=self.current_char() if self.pos < len(self.source) else "",
            source_lines=self.lines
        )
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self):
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
                self.at_line_start = True
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self, skip_newlines: bool = True):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
        
        if skip_newlines and self.current_char() == '\n':
            self.advance()
            self.skip_whitespace(skip_newlines=True)
    
    def skip_comment(self):
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_string(self) -> Tuple[str, int, int]:
        start_line = self.line
        start_column = self.column
        quote_char = self.current_char()
        self.advance()
        
        result = []
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char() in ('n', 't', 'r', '\\', '"', "'"):
                    escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'"}
                    result.append(escape_map.get(self.current_char(), self.current_char()))
                    self.advance()
                else:
                    result.append(self.current_char())
                    self.advance()
            else:
                result.append(self.current_char())
                self.advance()
        
        if not self.current_char():
            self.line = start_line
            self.column = start_column
            self.error("Guillemet de fermeture manquant", code="E101")
        
        self.advance()
        return ''.join(result), start_line, start_column
    
    def read_number(self) -> Tuple[TokenType, float, int, int]:
        start = self.pos
        start_line = self.line
        start_column = self.column
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot or not self.peek_char() or not self.peek_char().isdigit():
                    break
                has_dot = True
            self.advance()
        
        number_str = self.source[start:self.pos]
        
        if has_dot:
            return TokenType.NUMBER, float(number_str), start_line, start_column
        else:
            return TokenType.NUMBER, int(number_str), start_line, start_column
    
    def read_identifier(self) -> Tuple[TokenType, str, int, int]:
        start = self.pos
        start_line = self.line
        start_column = self.column
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        
        identifier = self.source[start:self.pos]
        
        identifier_lower = identifier.lower()
        
        if identifier_lower in KEYWORDS:
            token_type = KEYWORDS[identifier_lower]
            if token_type == TokenType.BOOLEAN:
                value = identifier_lower == 'vrai'
                return TokenType.BOOLEAN, value, start_line, start_column
            
            if identifier_lower == 'sinon':
                self.skip_whitespace(skip_newlines=False)
                if self.current_char() and self.pos + 2 < len(self.source):
                    next_word_match = re.match(r'si\b', self.source[self.pos:], re.IGNORECASE)
                    if next_word_match:
                        for _ in range(len(next_word_match.group())):
                            self.advance()
                        return TokenType.SINON_SI, 'sinon si', start_line, start_column
            
            if identifier_lower == 'tant':
                self.skip_whitespace(skip_newlines=False)
                if self.current_char() and self.pos + 3 < len(self.source):
                    next_word_match = re.match(r'que\b', self.source[self.pos:], re.IGNORECASE)
                    if next_word_match:
                        for _ in range(len(next_word_match.group())):
                            self.advance()
                        return TokenType.TANT_QUE, 'tant que', start_line, start_column
            
            if identifier_lower == 'pour':
                self.skip_whitespace(skip_newlines=False)
                if self.current_char() and self.pos + 6 < len(self.source):
                    next_word_match = re.match(r'chaque\b', self.source[self.pos:], re.IGNORECASE)
                    if next_word_match:
                        for _ in range(len(next_word_match.group())):
                            self.advance()
                        return TokenType.POUR_CHAQUE, 'pour chaque', start_line, start_column
            
            return token_type, identifier, start_line, start_column
        
        return TokenType.IDENTIFIER, identifier, start_line, start_column
    
    def handle_indentation(self, indent_level: int):
        current_indent = self.indent_stack[-1]
        
        if indent_level > current_indent:
            self.indent_stack.append(indent_level)
            self.tokens.append(Token(TokenType.INDENT, indent_level, self.line, 1))
        elif indent_level < current_indent:
            while self.indent_stack and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, indent_level, self.line, 1))
            
            if not self.indent_stack or self.indent_stack[-1] != indent_level:
                self.error("Indentation incorrecte", code="E103")
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            if self.at_line_start:
                indent_level = 0
                start_pos = self.pos
                
                while self.current_char() in ' \t':
                    if self.current_char() == ' ':
                        indent_level += 1
                    elif self.current_char() == '\t':
                        indent_level += 4
                    self.advance()
                
                if self.current_char() == '#':
                    self.skip_comment()
                    continue
                
                if self.current_char() == '\n':
                    self.advance()
                    continue
                
                if self.current_char() is None:
                    break
                
                self.handle_indentation(indent_level)
                self.at_line_start = False
                continue
            
            char = self.current_char()
            
            if char is None:
                break
            
            if char in ' \t\r':
                self.skip_whitespace(skip_newlines=False)
                continue
            
            if char == '#':
                self.skip_comment()
                continue
            
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                self.advance()
                continue
            
            if char in ('"', "'"):
                string_val, start_line, start_column = self.read_string()
                self.tokens.append(Token(TokenType.STRING, string_val, start_line, start_column))
                continue
            
            if char.isdigit():
                token_type, number_val, start_line, start_column = self.read_number()
                self.tokens.append(Token(token_type, number_val, start_line, start_column))
                continue
            
            if char.isalpha() or char == '_':
                token_type, value, start_line, start_column = self.read_identifier()
                self.tokens.append(Token(token_type, value, start_line, start_column))
                continue
            
            if char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', self.line, self.column))
                self.advance()
                continue
            
            if char == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', self.line, self.column))
                self.advance()
                continue
            
            if char == '*':
                if self.peek_char() == '*':
                    self.tokens.append(Token(TokenType.POWER, '**', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.MULTIPLY, '*', self.line, self.column))
                    self.advance()
                continue
            
            if char == '/':
                if self.peek_char() == '/':
                    self.tokens.append(Token(TokenType.FLOOR_DIV, '//', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.DIVIDE, '/', self.line, self.column))
                    self.advance()
                continue
            
            if char == '%':
                self.tokens.append(Token(TokenType.MODULO, '%', self.line, self.column))
                self.advance()
                continue
            
            if char == '=':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.EQUAL, '==', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', self.line, self.column))
                    self.advance()
                continue
            
            if char == '!':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    self.error("Opérateur inconnu: !", code="E100")
                continue
            
            if char == '<':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.LESS_THAN, '<', self.line, self.column))
                    self.advance()
                continue
            
            if char == '>':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.GREATER_THAN, '>', self.line, self.column))
                    self.advance()
                continue
            
            if char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', self.line, self.column))
                self.advance()
                continue
            
            if char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', self.line, self.column))
                self.advance()
                continue
            
            if char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', self.line, self.column))
                self.advance()
                continue
            
            if char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', self.line, self.column))
                self.advance()
                continue
            
            if char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', self.line, self.column))
                self.advance()
                continue
            
            if char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', self.line, self.column))
                self.advance()
                continue
            
            if char == '.':
                self.tokens.append(Token(TokenType.DOT, '.', self.line, self.column))
                self.advance()
                continue
            
            self.error(f"Caractère inattendu: {char}", code="E100")
        
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, 0, self.line, self.column))
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        
        return self.tokens


def tokenize(source: str, filename: str = "<script>") -> List[Token]:
    lexer = Lexer(source, filename)
    return lexer.tokenize()
