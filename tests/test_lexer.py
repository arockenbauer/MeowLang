"""
Tests pour le lexer MeowLang.
"""

import pytest
from meowlang.lexer import Lexer, TokenType, Token, tokenize
from meowlang.errors import MeowLangError


def test_empty_script():
    source = ""
    tokens = tokenize(source)
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF


def test_simple_miaou_meow():
    source = "miaou\nmeow"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.MIAOU
    assert tokens[1].type == TokenType.NEWLINE
    assert tokens[2].type == TokenType.MEOW
    assert tokens[3].type == TokenType.EOF


def test_ecrire_string():
    source = 'ecrire "Hello, chat!"'
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.ECRIRE
    assert tokens[1].type == TokenType.STRING
    assert tokens[1].value == "Hello, chat!"
    assert tokens[2].type == TokenType.EOF


def test_numbers():
    source = "42 3.14 0"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == 42
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[1].value == 3.14
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[2].value == 0


def test_identifiers():
    source = "nom age chat_123"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "nom"
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "age"
    assert tokens[2].type == TokenType.IDENTIFIER
    assert tokens[2].value == "chat_123"


def test_operators():
    source = "+ - * / // % ** = == != < > <= >="
    tokens = tokenize(source)
    
    expected_types = [
        TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
        TokenType.FLOOR_DIV, TokenType.MODULO, TokenType.POWER,
        TokenType.ASSIGN, TokenType.EQUAL, TokenType.NOT_EQUAL,
        TokenType.LESS_THAN, TokenType.GREATER_THAN,
        TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL,
        TokenType.EOF
    ]
    
    for i, expected_type in enumerate(expected_types):
        assert tokens[i].type == expected_type


def test_delimiters():
    source = ": , ( ) [ ]"
    tokens = tokenize(source)
    
    expected_types = [
        TokenType.COLON, TokenType.COMMA,
        TokenType.LPAREN, TokenType.RPAREN,
        TokenType.LBRACKET, TokenType.RBRACKET,
        TokenType.EOF
    ]
    
    for i, expected_type in enumerate(expected_types):
        assert tokens[i].type == expected_type


def test_keywords():
    source = "si alors sinon repeter fois tant que pour chaque dans"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.SI
    assert tokens[1].type == TokenType.ALORS
    assert tokens[2].type == TokenType.SINON
    assert tokens[3].type == TokenType.REPETER
    assert tokens[4].type == TokenType.FOIS
    assert tokens[5].type == TokenType.TANT_QUE
    assert tokens[5].value == "tant que"
    assert tokens[6].type == TokenType.POUR_CHAQUE
    assert tokens[6].value == "pour chaque"
    assert tokens[7].type == TokenType.DANS


def test_sinon_si():
    source = "si x alors:\n  ecrire \"oui\"\nsinon si y alors:\n  ecrire \"peut-etre\""
    tokens = tokenize(source)
    
    found_sinon_si = False
    for token in tokens:
        if token.type == TokenType.SINON_SI:
            found_sinon_si = True
            break
    
    assert found_sinon_si


def test_tant_que():
    source = "tant que x < 10:\n  x = x + 1"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.TANT_QUE
    assert tokens[0].value == "tant que"


def test_pour_chaque():
    source = "pour chaque item dans liste:\n  ecrire item"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.POUR_CHAQUE
    assert tokens[0].value == "pour chaque"


def test_booleans():
    source = "vrai faux"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.BOOLEAN
    assert tokens[0].value == True
    assert tokens[1].type == TokenType.BOOLEAN
    assert tokens[1].value == False


def test_logical_operators():
    source = "et ou non"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.ET
    assert tokens[1].type == TokenType.OU
    assert tokens[2].type == TokenType.NON


def test_comments():
    source = "ecrire \"test\"  # ceci est un commentaire\necrire \"suite\""
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.ECRIRE
    assert tokens[1].type == TokenType.STRING
    assert tokens[2].type == TokenType.NEWLINE
    assert tokens[3].type == TokenType.ECRIRE


def test_string_escapes():
    source = r'ecrire "Hello\nWorld\t!"'
    tokens = tokenize(source)
    
    assert tokens[1].type == TokenType.STRING
    assert tokens[1].value == "Hello\nWorld\t!"


def test_indentation_indent():
    source = "si vrai alors:\n  ecrire \"indente\""
    tokens = tokenize(source)
    
    found_indent = False
    for token in tokens:
        if token.type == TokenType.INDENT:
            found_indent = True
            break
    
    assert found_indent


def test_indentation_dedent():
    source = "si vrai alors:\n  ecrire \"indente\"\necrire \"plus indente\""
    tokens = tokenize(source)
    
    found_dedent = False
    for token in tokens:
        if token.type == TokenType.DEDENT:
            found_dedent = True
            break
    
    assert found_dedent


def test_multiple_indent_levels():
    source = """si vrai alors:
  si vrai alors:
    ecrire "niveau 2"
  ecrire "niveau 1"
ecrire "niveau 0"
"""
    tokens = tokenize(source)
    
    indent_count = sum(1 for t in tokens if t.type == TokenType.INDENT)
    dedent_count = sum(1 for t in tokens if t.type == TokenType.DEDENT)
    
    assert indent_count == 2
    assert dedent_count == 2


def test_line_and_column_tracking():
    source = "ecrire \"test\"\nx = 42"
    tokens = tokenize(source)
    
    assert tokens[0].line == 1
    assert tokens[0].column == 1
    
    for token in tokens:
        if token.type == TokenType.IDENTIFIER and token.value == "x":
            assert token.line == 2


def test_assignment():
    source = "x = 5"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "x"
    assert tokens[1].type == TokenType.ASSIGN
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[2].value == 5


def test_function_definition():
    source = "fonction saluer(nom):\n  ecrire nom"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.FONCTION
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "saluer"
    assert tokens[2].type == TokenType.LPAREN
    assert tokens[3].type == TokenType.IDENTIFIER
    assert tokens[3].value == "nom"
    assert tokens[4].type == TokenType.RPAREN
    assert tokens[5].type == TokenType.COLON


def test_list_syntax():
    source = 'liste("a", "b", "c")'
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.LISTE
    assert tokens[1].type == TokenType.LPAREN
    assert tokens[2].type == TokenType.STRING
    assert tokens[3].type == TokenType.COMMA


def test_dict_syntax():
    source = 'dictionnaire("nom":"Chat", "age":3)'
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.DICTIONNAIRE


def test_try_except():
    source = "essayer:\n  x = 10\nsauf erreur:\n  ecrire \"erreur\""
    tokens = tokenize(source)
    
    found_essayer = False
    found_sauf = False
    found_erreur = False
    
    for token in tokens:
        if token.type == TokenType.ESSAYER:
            found_essayer = True
        elif token.type == TokenType.SAUF:
            found_sauf = True
        elif token.type == TokenType.ERREUR:
            found_erreur = True
    
    assert found_essayer
    assert found_sauf
    assert found_erreur


def test_import():
    source = "importer math"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.IMPORTER
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "math"


def test_unterminated_string_error():
    source = 'ecrire "test sans fin'
    
    with pytest.raises(MeowLangError) as exc_info:
        tokenize(source)
    
    assert exc_info.value.error_def.code == "E101"


def test_case_insensitive_keywords():
    source = "ECRIRE Ecrire eCrIrE"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.ECRIRE
    assert tokens[1].type == TokenType.ECRIRE
    assert tokens[2].type == TokenType.ECRIRE


def test_compteur():
    source = "repeter 5 fois:\n  ecrire compteur"
    tokens = tokenize(source)
    
    found_compteur = False
    for token in tokens:
        if token.type == TokenType.COMPTEUR:
            found_compteur = True
            break
    
    assert found_compteur


def test_builtin_functions():
    source = "minuscule majuscule longueur remplacer contient"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.MINUSCULE
    assert tokens[1].type == TokenType.MAJUSCULE
    assert tokens[2].type == TokenType.LONGUEUR
    assert tokens[3].type == TokenType.REMPLACER
    assert tokens[4].type == TokenType.CONTIENT


def test_math_functions():
    source = "aleatoire sqrt abs round floor ceil"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.ALEATOIRE
    assert tokens[1].type == TokenType.SQRT
    assert tokens[2].type == TokenType.ABS
    assert tokens[3].type == TokenType.ROUND
    assert tokens[4].type == TokenType.FLOOR
    assert tokens[5].type == TokenType.CEIL


def test_file_operations():
    source = "ouvrir lire fermer"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.OUVRIR
    assert tokens[1].type == TokenType.LIRE
    assert tokens[2].type == TokenType.FERMER


def test_attendre():
    source = "attendre 2"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.ATTENDRE
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[1].value == 2


def test_aleatoire_a():
    source = "aleatoire 1 a 100"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.ALEATOIRE
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[2].type == TokenType.IDENTIFIER
    assert tokens[2].value == "a"
    assert tokens[3].type == TokenType.NUMBER


def test_complex_expression():
    source = "resultat = (3 + 5) * 2 ** 3 / 4"
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[1].type == TokenType.ASSIGN
    assert tokens[2].type == TokenType.LPAREN
    assert tokens[3].type == TokenType.NUMBER
    assert tokens[4].type == TokenType.PLUS
    assert tokens[5].type == TokenType.NUMBER
    assert tokens[6].type == TokenType.RPAREN
    assert tokens[7].type == TokenType.MULTIPLY
    assert tokens[8].type == TokenType.NUMBER
    assert tokens[9].type == TokenType.POWER
    assert tokens[10].type == TokenType.NUMBER
    assert tokens[11].type == TokenType.DIVIDE
    assert tokens[12].type == TokenType.NUMBER


def test_complete_script():
    source = """miaou
ecrire "Bonjour!"
nom = demander texte "Ton nom?"
si nom = "Chat" alors:
  ecrire "Miaou!"
sinon:
  ecrire "Humain détecté"
meow"""
    tokens = tokenize(source)
    
    assert tokens[0].type == TokenType.MIAOU
    
    meow_found = False
    for i, token in enumerate(tokens):
        if token.type == TokenType.MEOW:
            meow_found = True
            assert i < len(tokens) - 1
            break
    
    assert meow_found
    assert tokens[-1].type == TokenType.EOF
    
    assert any(t.type == TokenType.INDENT for t in tokens)
    assert any(t.type == TokenType.DEDENT for t in tokens)
