"""
Tests pour le parser MeowLang.
"""

import pytest
from meowlang.parser import Parser, parse
from meowlang.lexer import Lexer, TokenType
from meowlang.ast_nodes import *
from meowlang.errors import MeowLangError


def parse_code(code: str) -> Program:
    """Helper pour parser du code."""
    return parse(code, filename="<test>")


def test_parser_simple_program():
    """Test parsing programme simple."""
    code = """miaou
ecrire "Hello"
meow"""
    
    program = parse_code(code)
    
    assert isinstance(program, Program)
    assert len(program.statements) == 1
    assert isinstance(program.statements[0], ExpressionStatement)


def test_parser_missing_miaou():
    """Test erreur si miaou manquant."""
    code = """ecrire "Hello"
meow"""
    
    with pytest.raises(MeowLangError) as exc_info:
        parse_code(code)
    
    assert exc_info.value.error_def.code == "E000"


def test_parser_missing_meow():
    """Test erreur si meow manquant."""
    code = """miaou
ecrire "Hello"
"""
    
    with pytest.raises(MeowLangError) as exc_info:
        parse_code(code)
    
    assert exc_info.value.error_def.code == "E001"


def test_parser_assignment():
    """Test parsing assignation."""
    code = """miaou
x = 5
nom = "Axel"
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 2
    assert isinstance(program.statements[0], Assignment)
    assert program.statements[0].name == "x"
    assert isinstance(program.statements[0].value, Literal)
    assert program.statements[0].value.value == 5


def test_parser_arithmetic_expressions():
    """Test parsing expressions arithmétiques avec priorité."""
    code = """miaou
x = 2 + 3 * 4
y = (2 + 3) * 4
z = 2 ** 3 + 1
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 3
    
    x_expr = program.statements[0].value
    assert isinstance(x_expr, BinaryOp)
    assert x_expr.operator == "+"
    assert isinstance(x_expr.right, BinaryOp)
    assert x_expr.right.operator == "*"


def test_parser_comparison_expressions():
    """Test parsing comparaisons."""
    code = """miaou
resultat = age >= 18
egal = nom == "Axel"
different = x != 5
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 3
    assert isinstance(program.statements[0].value, BinaryOp)
    assert program.statements[0].value.operator == ">="


def test_parser_logical_expressions():
    """Test parsing expressions logiques."""
    code = """miaou
resultat = age >= 18 et nom == "Axel"
autre = x > 5 ou y < 10
negation = non vrai
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 3
    assert isinstance(program.statements[0].value, BinaryOp)
    assert program.statements[0].value.operator == "et"
    assert isinstance(program.statements[2].value, UnaryOp)
    assert program.statements[2].value.operator == "non"


def test_parser_if_statement():
    """Test parsing if."""
    code = """miaou
si age < 18 alors:
  ecrire "Jeune"
sinon:
  ecrire "Adulte"
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, IfStatement)
    assert isinstance(stmt.condition, BinaryOp)
    assert len(stmt.then_block) == 1
    assert stmt.else_block is not None
    assert len(stmt.else_block) == 1


def test_parser_if_elif_else():
    """Test parsing if/elif/else."""
    code = """miaou
si age < 10 alors:
  ecrire "Enfant"
sinon si age < 18 alors:
  ecrire "Ado"
sinon:
  ecrire "Adulte"
meow"""
    
    program = parse_code(code)
    
    stmt = program.statements[0]
    assert isinstance(stmt, IfStatement)
    assert len(stmt.elif_blocks) == 1
    assert stmt.else_block is not None


def test_parser_while_loop():
    """Test parsing while."""
    code = """miaou
x = 0
tant que x < 5:
  x = x + 1
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 2
    loop = program.statements[1]
    assert isinstance(loop, WhileLoop)
    assert isinstance(loop.condition, BinaryOp)
    assert len(loop.body) == 1


def test_parser_repeat_loop():
    """Test parsing repeat."""
    code = """miaou
repeter 5 fois:
  ecrire compteur
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 1
    loop = program.statements[0]
    assert isinstance(loop, RepeatLoop)
    assert isinstance(loop.count, Literal)
    assert loop.count.value == 5
    assert len(loop.body) == 1


def test_parser_foreach_loop():
    """Test parsing for each."""
    code = """miaou
pour chaque chat dans chats:
  ecrire chat
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 1
    loop = program.statements[0]
    assert isinstance(loop, ForEachLoop)
    assert loop.iterator == "chat"
    assert isinstance(loop.iterable, Identifier)
    assert loop.iterable.name == "chats"
    assert len(loop.body) == 1


def test_parser_function_definition():
    """Test parsing définition de fonction."""
    code = """miaou
fonction saluer(nom):
  ecrire "Bonjour " nom
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 1
    func = program.statements[0]
    assert isinstance(func, FunctionDef)
    assert func.name == "saluer"
    assert func.parameters == ["nom"]
    assert len(func.body) == 1


def test_parser_function_call():
    """Test parsing appel de fonction."""
    code = """miaou
saluer("Axel")
addition(3, 7)
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 2
    
    call1 = program.statements[0].expression
    assert isinstance(call1, FunctionCall)
    assert call1.name == "saluer"
    assert len(call1.arguments) == 1
    
    call2 = program.statements[1].expression
    assert isinstance(call2, FunctionCall)
    assert call2.name == "addition"
    assert len(call2.arguments) == 2


def test_parser_return_statement():
    """Test parsing return."""
    code = """miaou
fonction double(x):
  retour x * 2
meow"""
    
    program = parse_code(code)
    
    func = program.statements[0]
    ret_stmt = func.body[0]
    assert isinstance(ret_stmt, ReturnStatement)
    assert isinstance(ret_stmt.value, BinaryOp)


def test_parser_liste():
    """Test parsing liste."""
    code = """miaou
chats = liste("Minou", "Pixel", "Salem")
nombres = liste(1, 2, 3)
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 2
    
    list_val = program.statements[0].value
    assert isinstance(list_val, ListNode)
    assert len(list_val.elements) == 3


def test_parser_dictionnaire():
    """Test parsing dictionnaire."""
    code = """miaou
infos = dictionnaire("nom":"Axel", "age":25)
meow"""
    
    program = parse_code(code)
    
    dict_val = program.statements[0].value
    assert isinstance(dict_val, DictNode)
    assert len(dict_val.pairs) == 2


def test_parser_index_access():
    """Test parsing accès par index."""
    code = """miaou
x = chats[0]
y = infos["nom"]
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 2
    
    idx_access = program.statements[0].value
    assert isinstance(idx_access, IndexAccess)
    assert isinstance(idx_access.object, Identifier)
    assert isinstance(idx_access.index, Literal)


def test_parser_index_assignment():
    """Test parsing assignation par index."""
    code = """miaou
chats[0] = "Minou"
infos["nom"] = "Pixel"
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 2
    
    idx_assign = program.statements[0]
    assert isinstance(idx_assign, IndexAssignment)
    assert isinstance(idx_assign.object, Identifier)
    assert isinstance(idx_assign.value, Literal)


def test_parser_try_except():
    """Test parsing try/except."""
    code = """miaou
essayer:
  resultat = 10 / nombre
sauf erreur:
  ecrire "Division interdite"
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 1
    
    try_stmt = program.statements[0]
    assert isinstance(try_stmt, TryExcept)
    assert len(try_stmt.try_block) == 1
    assert len(try_stmt.except_block) == 1


def test_parser_import():
    """Test parsing import."""
    code = """miaou
importer math
importer chats_utils
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 2
    
    import1 = program.statements[0]
    assert isinstance(import1, ImportStatement)
    assert import1.module_name == "math"


def test_parser_demander():
    """Test parsing demander."""
    code = """miaou
nom = demander texte "Ton nom ?"
age = demander nombre "Ton âge ?"
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 2
    
    call1 = program.statements[0].value
    assert isinstance(call1, FunctionCall)
    assert call1.name == "demander_texte"
    
    call2 = program.statements[1].value
    assert isinstance(call2, FunctionCall)
    assert call2.name == "demander_nombre"


def test_parser_aleatoire():
    """Test parsing aleatoire."""
    code = """miaou
chance = aleatoire 1 a 100
meow"""
    
    program = parse_code(code)
    
    call = program.statements[0].value
    assert isinstance(call, FunctionCall)
    assert call.name == "aleatoire"
    assert len(call.arguments) == 2


def test_parser_builtin_functions():
    """Test parsing fonctions built-in."""
    code = """miaou
texte = minuscule "HELLO"
val = sqrt 16
resultat = abs(-5)
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 3
    
    call1 = program.statements[0].value
    assert isinstance(call1, FunctionCall)
    assert call1.name == "minuscule"
    
    call2 = program.statements[1].value
    assert isinstance(call2, FunctionCall)
    assert call2.name == "sqrt"


def test_parser_attribute_access():
    """Test parsing accès attribut (module.fonction)."""
    code = """miaou
importer math
x = math.sqrt(16)
meow"""
    
    program = parse_code(code)
    
    call = program.statements[1].value
    assert isinstance(call, FunctionCall)
    assert "math" in call.name and "sqrt" in call.name


def test_parser_nested_blocks():
    """Test parsing blocs imbriqués."""
    code = """miaou
si x > 0:
  si y > 0:
    ecrire "Positifs"
  sinon:
    ecrire "X positif"
meow"""
    
    program = parse_code(code)
    
    outer_if = program.statements[0]
    assert isinstance(outer_if, IfStatement)
    
    inner_if = outer_if.then_block[0]
    assert isinstance(inner_if, IfStatement)


def test_parser_complex_expression():
    """Test parsing expression complexe."""
    code = """miaou
resultat = (a + b) * (c - d) / e ** 2
meow"""
    
    program = parse_code(code)
    
    expr = program.statements[0].value
    assert isinstance(expr, BinaryOp)


def test_parser_ecrire_multiple_args():
    """Test parsing ecrire avec plusieurs arguments."""
    code = """miaou
ecrire "Bonjour " nom " !"
meow"""
    
    program = parse_code(code)
    
    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)
    call = stmt.expression
    assert isinstance(call, FunctionCall)
    assert call.name == "ecrire"
    assert len(call.arguments) == 3


def test_parser_parenthesized_expression():
    """Test parsing expression parenthésée."""
    code = """miaou
x = (5 + 3)
y = ((2 + 3) * 4)
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 2
    assert isinstance(program.statements[0].value, BinaryOp)


def test_parser_compteur_identifier():
    """Test parsing identifiant 'compteur'."""
    code = """miaou
repeter 5 fois:
  ecrire compteur
meow"""
    
    program = parse_code(code)
    
    loop = program.statements[0]
    ecrire_stmt = loop.body[0]
    call = ecrire_stmt.expression
    compteur_arg = call.arguments[0]
    assert isinstance(compteur_arg, Identifier)
    assert compteur_arg.name == "compteur"


def test_parser_empty_function():
    """Test parsing fonction vide."""
    code = """miaou
fonction vide():
  x = 0
meow"""
    
    program = parse_code(code)
    
    func = program.statements[0]
    assert isinstance(func, FunctionDef)
    assert func.parameters == []


def test_parser_multiple_parameters():
    """Test parsing fonction avec plusieurs paramètres."""
    code = """miaou
fonction calculer(a, b, c):
  retour a + b + c
meow"""
    
    program = parse_code(code)
    
    func = program.statements[0]
    assert len(func.parameters) == 3
    assert func.parameters == ["a", "b", "c"]


def test_parser_unary_minus():
    """Test parsing moins unaire."""
    code = """miaou
x = -5
y = -(a + b)
meow"""
    
    program = parse_code(code)
    
    assert len(program.statements) == 2
    
    unary1 = program.statements[0].value
    assert isinstance(unary1, UnaryOp)
    assert unary1.operator == "-"


def test_parser_power_associativity():
    """Test parsing associativité puissance (right-associative)."""
    code = """miaou
x = 2 ** 3 ** 2
meow"""
    
    program = parse_code(code)
    
    expr = program.statements[0].value
    assert isinstance(expr, BinaryOp)
    assert expr.operator == "**"
    assert isinstance(expr.right, BinaryOp)
    assert expr.right.operator == "**"


def test_parser_missing_colon():
    """Test erreur si ':' manquant."""
    code = """miaou
si age > 18
  ecrire "Adulte"
meow"""
    
    with pytest.raises(MeowLangError) as exc_info:
        parse_code(code)
    
    assert exc_info.value.error_def.code == "E104"


def test_parser_missing_indent():
    """Test erreur si indentation manquante."""
    code = """miaou
si age > 18:
ecrire "Adulte"
meow"""
    
    with pytest.raises(MeowLangError) as exc_info:
        parse_code(code)
    
    assert exc_info.value.error_def.code == "E103"


def test_parser_missing_parenthesis():
    """Test erreur si parenthèse manquante."""
    code = """miaou
fonction test(a, b:
  retour a + b
meow"""
    
    with pytest.raises(MeowLangError) as exc_info:
        parse_code(code)
    
    assert exc_info.value.error_def.code == "E102"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
