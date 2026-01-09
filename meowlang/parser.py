"""
Parser pour MeowLang - Construction de l'AST à partir des tokens.
"""

from typing import List, Optional, Tuple
from .lexer import Token, TokenType
from .ast_nodes import *
from .errors import ErrorCatalog


class Parser:
    def __init__(self, tokens: List[Token], filename: str = "<script>", source_lines: List[str] = None):
        self.tokens = tokens
        self.filename = filename
        self.source_lines = source_lines or []
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
    
    def error(self, message: str, code: str = "E100", **kwargs):
        """Lève une erreur de parsing."""
        ErrorCatalog.raise_error(
            code=code,
            file=self.filename,
            line=self.current_token.line if self.current_token else 1,
            column=self.current_token.column if self.current_token else 1,
            instruction=str(self.current_token.value) if self.current_token else "",
            source_lines=self.source_lines,
            **kwargs
        )
    
    def advance(self):
        """Avance au token suivant."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Regarde le token à position actuelle + offset."""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: TokenType, error_code: str = "E100") -> Token:
        """Vérifie que le token actuel est du type attendu, sinon erreur."""
        if not self.current_token or self.current_token.type != token_type:
            self.error(
                f"Token {token_type.name} attendu, trouvé {self.current_token.type.name if self.current_token else 'EOF'}",
                code=error_code
            )
        token = self.current_token
        self.advance()
        return token
    
    def skip_newlines(self):
        """Saute les newlines optionnels."""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
    
    def current_position(self) -> Position:
        """Retourne la position actuelle."""
        if self.current_token:
            return Position(self.current_token.line, self.current_token.column)
        return Position(1, 1)
    
    def parse(self) -> Program:
        """Parse le programme complet."""
        pos = self.current_position()
        
        self.skip_newlines()
        
        if not self.current_token or self.current_token.type != TokenType.MIAOU:
            self.error("Le script doit commencer par 'miaou'", code="E000")
        
        self.advance()
        self.skip_newlines()
        
        statements = []
        while self.current_token and self.current_token.type not in (TokenType.MEOW, TokenType.EOF):
            if self.current_token.type == TokenType.NEWLINE:
                self.skip_newlines()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            
            self.skip_newlines()
            
            if not self.current_token:
                break
        
        if not self.current_token or self.current_token.type != TokenType.MEOW:
            self.error("Le script doit se terminer par 'meow'", code="E001")
        
        return Program(position=pos, statements=statements)
    
    def parse_statement(self):
        """Parse un statement."""
        self.skip_newlines()
        
        if not self.current_token:
            return None
        
        token_type = self.current_token.type
        
        if token_type == TokenType.ECRIRE:
            return self.parse_ecrire()
        elif token_type == TokenType.SI:
            return self.parse_if()
        elif token_type == TokenType.TANT_QUE:
            return self.parse_while()
        elif token_type == TokenType.REPETER:
            return self.parse_repeat()
        elif token_type == TokenType.POUR_CHAQUE:
            return self.parse_foreach()
        elif token_type == TokenType.FONCTION:
            return self.parse_function_def()
        elif token_type == TokenType.RETOUR:
            return self.parse_return()
        elif token_type == TokenType.ESSAYER:
            return self.parse_try_except()
        elif token_type == TokenType.IMPORTER:
            return self.parse_import()
        elif token_type == TokenType.IDENTIFIER:
            return self.parse_assignment_or_expression()
        elif token_type in (TokenType.DEDENT, TokenType.EOF, TokenType.MEOW):
            return None
        else:
            expr = self.parse_expression()
            return ExpressionStatement(position=expr.position, expression=expr)
    
    def parse_ecrire(self) -> ExpressionStatement:
        """Parse 'ecrire' statement."""
        pos = self.current_position()
        self.advance()
        
        args = []
        while self.current_token and self.current_token.type not in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            old_pos = self.pos
            args.append(self.parse_additive_expression())
            
            if self.pos == old_pos:
                break
        
        call = FunctionCall(position=pos, name="ecrire", arguments=args)
        return ExpressionStatement(position=pos, expression=call)
    
    def parse_assignment_or_expression(self):
        """Parse assignment (x = 5) ou expression (fonction())."""
        pos = self.current_position()
        
        if self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            next_token = self.peek()
            
            if next_token and next_token.type == TokenType.ASSIGN:
                self.advance()
                self.advance()
                
                value = self.parse_expression()
                return Assignment(position=pos, name=name, value=value)
            
            elif next_token and next_token.type == TokenType.LBRACKET:
                obj_expr = self.parse_postfix_expression()
                
                if self.current_token and self.current_token.type == TokenType.ASSIGN:
                    self.advance()
                    value = self.parse_expression()
                    
                    if isinstance(obj_expr, IndexAccess):
                        return IndexAssignment(
                            position=pos,
                            object=obj_expr.object,
                            index=obj_expr.index,
                            value=value
                        )
                
                return ExpressionStatement(position=pos, expression=obj_expr)
        
        expr = self.parse_expression()
        return ExpressionStatement(position=pos, expression=expr)
    
    def parse_if(self) -> IfStatement:
        """Parse 'si' statement."""
        pos = self.current_position()
        self.advance()
        
        condition = self.parse_expression()
        
        if self.current_token and self.current_token.type == TokenType.ALORS:
            self.advance()
        
        self.expect(TokenType.COLON, error_code="E104")
        self.skip_newlines()
        
        then_block = self.parse_block()
        
        elif_blocks = []
        else_block = None
        
        while self.current_token and self.current_token.type == TokenType.SINON_SI:
            self.advance()
            elif_condition = self.parse_expression()
            
            if self.current_token and self.current_token.type == TokenType.ALORS:
                self.advance()
            
            self.expect(TokenType.COLON, error_code="E104")
            self.skip_newlines()
            
            elif_body = self.parse_block()
            elif_blocks.append((elif_condition, elif_body))
        
        if self.current_token and self.current_token.type == TokenType.SINON:
            self.advance()
            self.expect(TokenType.COLON, error_code="E104")
            self.skip_newlines()
            else_block = self.parse_block()
        
        return IfStatement(
            position=pos,
            condition=condition,
            then_block=then_block,
            elif_blocks=elif_blocks,
            else_block=else_block
        )
    
    def parse_while(self) -> WhileLoop:
        """Parse 'tant que' loop."""
        pos = self.current_position()
        self.advance()
        
        condition = self.parse_expression()
        
        self.expect(TokenType.COLON, error_code="E104")
        self.skip_newlines()
        
        body = self.parse_block()
        
        return WhileLoop(position=pos, condition=condition, body=body)
    
    def parse_repeat(self) -> RepeatLoop:
        """Parse 'repeter N fois' loop."""
        pos = self.current_position()
        self.advance()
        
        count = self.parse_expression()
        
        if self.current_token and self.current_token.type == TokenType.FOIS:
            self.advance()
        
        self.expect(TokenType.COLON, error_code="E104")
        self.skip_newlines()
        
        body = self.parse_block()
        
        return RepeatLoop(position=pos, count=count, body=body)
    
    def parse_foreach(self) -> ForEachLoop:
        """Parse 'pour chaque x dans liste' loop."""
        pos = self.current_position()
        self.advance()
        
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            self.error("Variable d'itération attendue", code="E104")
        
        iterator = self.current_token.value
        self.advance()
        
        if self.current_token and self.current_token.type == TokenType.DANS:
            self.advance()
        else:
            self.error("'dans' attendu après variable d'itération", code="E104")
        
        iterable = self.parse_expression()
        
        self.expect(TokenType.COLON, error_code="E104")
        self.skip_newlines()
        
        body = self.parse_block()
        
        return ForEachLoop(position=pos, iterator=iterator, iterable=iterable, body=body)
    
    def parse_function_def(self) -> FunctionDef:
        """Parse 'fonction nom(params):'."""
        pos = self.current_position()
        self.advance()
        
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            self.error("Nom de fonction attendu", code="E104")
        
        name = self.current_token.value
        self.advance()
        
        self.expect(TokenType.LPAREN, error_code="E102")
        
        parameters = []
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Nom de paramètre attendu", code="E104")
            
            parameters.append(self.current_token.value)
            self.advance()
            
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
            elif self.current_token and self.current_token.type != TokenType.RPAREN:
                self.error("',' ou ')' attendu", code="E102")
        
        self.expect(TokenType.RPAREN, error_code="E102")
        self.expect(TokenType.COLON, error_code="E104")
        self.skip_newlines()
        
        body = self.parse_block()
        
        return FunctionDef(position=pos, name=name, parameters=parameters, body=body)
    
    def parse_return(self) -> ReturnStatement:
        """Parse 'retour valeur'."""
        pos = self.current_position()
        self.advance()
        
        value = None
        if self.current_token and self.current_token.type not in (TokenType.NEWLINE, TokenType.EOF):
            value = self.parse_expression()
        
        return ReturnStatement(position=pos, value=value)
    
    def parse_try_except(self) -> TryExcept:
        """Parse 'essayer: ... sauf erreur: ...'."""
        pos = self.current_position()
        self.advance()
        
        self.expect(TokenType.COLON, error_code="E104")
        self.skip_newlines()
        
        try_block = self.parse_block()
        
        if not self.current_token or self.current_token.type != TokenType.SAUF:
            self.error("'sauf' attendu après bloc 'essayer'", code="E104")
        
        self.advance()
        
        if self.current_token and self.current_token.type == TokenType.ERREUR:
            self.advance()
        
        self.expect(TokenType.COLON, error_code="E104")
        self.skip_newlines()
        
        except_block = self.parse_block()
        
        return TryExcept(position=pos, try_block=try_block, except_block=except_block)
    
    def parse_import(self) -> ImportStatement:
        """Parse 'importer module'."""
        pos = self.current_position()
        self.advance()
        
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            self.error("Nom de module attendu", code="E104")
        
        module_name = self.current_token.value
        self.advance()
        
        return ImportStatement(position=pos, module_name=module_name)
    
    def parse_block(self) -> List[ASTNode]:
        """Parse un bloc indenté de statements."""
        if not self.current_token or self.current_token.type != TokenType.INDENT:
            self.error("Bloc indenté attendu", code="E103")
        
        self.advance()
        statements = []
        
        while self.current_token and self.current_token.type != TokenType.DEDENT:
            if self.current_token.type == TokenType.NEWLINE:
                self.skip_newlines()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            
            self.skip_newlines()
        
        if self.current_token and self.current_token.type == TokenType.DEDENT:
            self.advance()
        
        return statements
    
    def parse_expression(self) -> ASTNode:
        """Parse une expression (point d'entrée)."""
        return self.parse_or_expression()
    
    def parse_or_expression(self) -> ASTNode:
        """Parse expression 'ou' (priorité la plus basse)."""
        left = self.parse_and_expression()
        
        while self.current_token and self.current_token.type == TokenType.OU:
            pos = self.current_position()
            self.advance()
            right = self.parse_and_expression()
            left = BinaryOp(position=pos, left=left, operator="ou", right=right)
        
        return left
    
    def parse_and_expression(self) -> ASTNode:
        """Parse expression 'et'."""
        left = self.parse_not_expression()
        
        while self.current_token and self.current_token.type == TokenType.ET:
            pos = self.current_position()
            self.advance()
            right = self.parse_not_expression()
            left = BinaryOp(position=pos, left=left, operator="et", right=right)
        
        return left
    
    def parse_not_expression(self) -> ASTNode:
        """Parse expression 'non'."""
        if self.current_token and self.current_token.type == TokenType.NON:
            pos = self.current_position()
            self.advance()
            operand = self.parse_not_expression()
            return UnaryOp(position=pos, operator="non", operand=operand)
        
        return self.parse_comparison_expression()
    
    def parse_comparison_expression(self) -> ASTNode:
        """Parse comparaisons (=, !=, <, >, <=, >=)."""
        left = self.parse_additive_expression()
        
        comparison_ops = {
            TokenType.ASSIGN: "=",
            TokenType.EQUAL: "==",
            TokenType.NOT_EQUAL: "!=",
            TokenType.LESS_THAN: "<",
            TokenType.GREATER_THAN: ">",
            TokenType.LESS_EQUAL: "<=",
            TokenType.GREATER_EQUAL: ">="
        }
        
        while self.current_token and self.current_token.type in comparison_ops:
            pos = self.current_position()
            op = comparison_ops[self.current_token.type]
            self.advance()
            right = self.parse_additive_expression()
            left = BinaryOp(position=pos, left=left, operator=op, right=right)
        
        return left
    
    def parse_additive_expression(self) -> ASTNode:
        """Parse addition/soustraction."""
        left = self.parse_multiplicative_expression()
        
        while self.current_token and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            pos = self.current_position()
            op = "+" if self.current_token.type == TokenType.PLUS else "-"
            self.advance()
            right = self.parse_multiplicative_expression()
            left = BinaryOp(position=pos, left=left, operator=op, right=right)
        
        return left
    
    def parse_multiplicative_expression(self) -> ASTNode:
        """Parse multiplication/division/modulo."""
        left = self.parse_power_expression()
        
        ops = {
            TokenType.MULTIPLY: "*",
            TokenType.DIVIDE: "/",
            TokenType.FLOOR_DIV: "//",
            TokenType.MODULO: "%"
        }
        
        while self.current_token and self.current_token.type in ops:
            pos = self.current_position()
            op = ops[self.current_token.type]
            self.advance()
            right = self.parse_power_expression()
            left = BinaryOp(position=pos, left=left, operator=op, right=right)
        
        return left
    
    def parse_power_expression(self) -> ASTNode:
        """Parse puissance (**)."""
        left = self.parse_unary_expression()
        
        if self.current_token and self.current_token.type == TokenType.POWER:
            pos = self.current_position()
            self.advance()
            right = self.parse_power_expression()
            return BinaryOp(position=pos, left=left, operator="**", right=right)
        
        return left
    
    def parse_unary_expression(self) -> ASTNode:
        """Parse expressions unaires (-, +)."""
        if self.current_token and self.current_token.type in (TokenType.MINUS, TokenType.PLUS):
            pos = self.current_position()
            op = "-" if self.current_token.type == TokenType.MINUS else "+"
            self.advance()
            operand = self.parse_unary_expression()
            return UnaryOp(position=pos, operator=op, operand=operand)
        
        return self.parse_postfix_expression()
    
    def parse_postfix_expression(self) -> ASTNode:
        """Parse expressions postfixées (appel de fonction, indexation, attributs)."""
        expr = self.parse_primary_expression()
        
        while True:
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                pos = self.current_position()
                self.advance()
                
                arguments = []
                while self.current_token and self.current_token.type != TokenType.RPAREN:
                    arguments.append(self.parse_expression())
                    
                    if self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()
                    elif self.current_token and self.current_token.type != TokenType.RPAREN:
                        break
                
                self.expect(TokenType.RPAREN, error_code="E102")
                
                if isinstance(expr, Identifier):
                    expr = FunctionCall(position=pos, name=expr.name, arguments=arguments)
                elif isinstance(expr, AttributeAccess):
                    expr = FunctionCall(position=pos, name=f"{expr.object}.{expr.attribute}", arguments=arguments)
            
            elif self.current_token and self.current_token.type == TokenType.LBRACKET:
                pos = self.current_position()
                self.advance()
                
                index = self.parse_expression()
                
                self.expect(TokenType.RBRACKET, error_code="E102")
                
                expr = IndexAccess(position=pos, object=expr, index=index)
            
            elif self.current_token and self.current_token.type == TokenType.DOT:
                pos = self.current_position()
                self.advance()
                
                if not self.current_token:
                    self.error("Attribut attendu après '.'", code="E104")
                
                if self.current_token.type not in (TokenType.IDENTIFIER, TokenType.SQRT, TokenType.ABS, 
                                                     TokenType.ROUND, TokenType.FLOOR, TokenType.CEIL,
                                                     TokenType.MINUSCULE, TokenType.MAJUSCULE, TokenType.LONGUEUR,
                                                     TokenType.REMPLACER, TokenType.CONTIENT, TokenType.ALEATOIRE,
                                                     TokenType.OUVRIR, TokenType.LIRE, TokenType.FERMER, TokenType.ATTENDRE):
                    self.error("Attribut attendu après '.'", code="E104")
                
                attribute = self.current_token.value if isinstance(self.current_token.value, str) else self.current_token.type.name.lower()
                self.advance()
                
                expr = AttributeAccess(position=pos, object=expr, attribute=attribute)
            
            else:
                break
        
        return expr
    
    def parse_primary_expression(self) -> ASTNode:
        """Parse expressions primaires (littéraux, identifiants, parenthèses, built-ins)."""
        pos = self.current_position()
        
        if not self.current_token:
            self.error("Expression attendue", code="E100")
        
        if self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            return Literal(position=pos, value=value, literal_type="number")
        
        elif self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            return Literal(position=pos, value=value, literal_type="string")
        
        elif self.current_token.type == TokenType.BOOLEAN:
            value = self.current_token.value
            self.advance()
            return Literal(position=pos, value=value, literal_type="boolean")
        
        elif self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            return Identifier(position=pos, name=name)
        
        elif self.current_token.type == TokenType.COMPTEUR:
            self.advance()
            return Identifier(position=pos, name="compteur")
        
        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, error_code="E102")
            return expr
        
        elif self.current_token.type == TokenType.LISTE:
            return self.parse_liste()
        
        elif self.current_token.type == TokenType.DICTIONNAIRE:
            return self.parse_dictionnaire()
        
        elif self.current_token.type == TokenType.DEMANDER:
            return self.parse_demander()
        
        elif self.current_token.type == TokenType.ALEATOIRE:
            return self.parse_aleatoire()
        
        elif self.current_token.type in (
            TokenType.MINUSCULE, TokenType.MAJUSCULE, TokenType.LONGUEUR,
            TokenType.SQRT, TokenType.ABS, TokenType.ROUND, TokenType.FLOOR, TokenType.CEIL,
            TokenType.OUVRIR, TokenType.LIRE, TokenType.FERMER, TokenType.ATTENDRE,
            TokenType.REMPLACER, TokenType.CONTIENT
        ):
            return self.parse_builtin_function()
        
        else:
            self.error(f"Expression inattendue: {self.current_token.type.name}", code="E100")
    
    def parse_liste(self) -> ListNode:
        """Parse 'liste(val1, val2, ...)'."""
        pos = self.current_position()
        self.advance()
        
        self.expect(TokenType.LPAREN, error_code="E102")
        
        elements = []
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            elements.append(self.parse_expression())
            
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
            elif self.current_token and self.current_token.type != TokenType.RPAREN:
                break
        
        self.expect(TokenType.RPAREN, error_code="E102")
        
        return ListNode(position=pos, elements=elements)
    
    def parse_dictionnaire(self) -> DictNode:
        """Parse 'dictionnaire("clé":val, ...)'."""
        pos = self.current_position()
        self.advance()
        
        self.expect(TokenType.LPAREN, error_code="E102")
        
        pairs = []
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            key = self.parse_expression()
            
            self.expect(TokenType.COLON, error_code="E104")
            
            value = self.parse_expression()
            pairs.append((key, value))
            
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
            elif self.current_token and self.current_token.type != TokenType.RPAREN:
                break
        
        self.expect(TokenType.RPAREN, error_code="E102")
        
        return DictNode(position=pos, pairs=pairs)
    
    def parse_demander(self) -> FunctionCall:
        """Parse 'demander texte/nombre "question"'."""
        pos = self.current_position()
        self.advance()
        
        func_name = "demander_texte"
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            type_name = self.current_token.value.lower()
            if type_name == "nombre":
                func_name = "demander_nombre"
            self.advance()
        
        prompt = self.parse_expression()
        
        return FunctionCall(position=pos, name=func_name, arguments=[prompt])
    
    def parse_aleatoire(self) -> FunctionCall:
        """Parse 'aleatoire min a max'."""
        pos = self.current_position()
        self.advance()
        
        min_val = self.parse_additive_expression()
        
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.value.lower() == 'a':
            self.advance()
        
        max_val = self.parse_additive_expression()
        
        return FunctionCall(position=pos, name="aleatoire", arguments=[min_val, max_val])
    
    def parse_builtin_function(self) -> FunctionCall:
        """Parse appel de fonction built-in (minuscule, sqrt, etc.)."""
        pos = self.current_position()
        
        function_map = {
            TokenType.MINUSCULE: "minuscule",
            TokenType.MAJUSCULE: "majuscule",
            TokenType.LONGUEUR: "longueur",
            TokenType.REMPLACER: "remplacer",
            TokenType.CONTIENT: "contient",
            TokenType.SQRT: "sqrt",
            TokenType.ABS: "abs",
            TokenType.ROUND: "round",
            TokenType.FLOOR: "floor",
            TokenType.CEIL: "ceil",
            TokenType.OUVRIR: "ouvrir",
            TokenType.LIRE: "lire",
            TokenType.FERMER: "fermer",
            TokenType.ATTENDRE: "attendre"
        }
        
        func_name = function_map.get(self.current_token.type)
        self.advance()
        
        arguments = []
        
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            self.advance()
            
            while self.current_token and self.current_token.type != TokenType.RPAREN:
                arguments.append(self.parse_expression())
                
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                elif self.current_token and self.current_token.type != TokenType.RPAREN:
                    break
            
            self.expect(TokenType.RPAREN, error_code="E102")
        else:
            arg = self.parse_postfix_expression()
            arguments.append(arg)
        
        return FunctionCall(position=pos, name=func_name, arguments=arguments)


def parse(source: str, filename: str = "<script>") -> Program:
    """Fonction helper pour parser du code MeowLang."""
    from .lexer import Lexer
    
    lines = source.split('\n')
    lexer = Lexer(source, filename)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens, filename, lines)
    return parser.parse()
