"""
Tests pour le système d'erreurs MeowLang.
"""

import pytest
from meowlang.errors import (
    MeowLangError,
    ErrorCatalog,
    ErrorSeverity,
    extract_context
)


def test_error_catalog_has_all_codes():
    """Vérifie que tous les codes d'erreur critiques sont enregistrés."""
    critical_codes = ["E000", "E001", "E100", "E200", "E500", "E600", "E700", "E900"]
    
    for code in critical_codes:
        error_def = ErrorCatalog.get(code)
        assert error_def is not None, f"Code {code} devrait être enregistré"
        assert error_def.code == code


def test_error_formatting_basic():
    """Test le formatage basique d'une erreur."""
    error_def = ErrorCatalog.get("E500")
    error = MeowLangError(
        error_def=error_def,
        file="test.miaou",
        line=10,
        column=5,
        instruction="10 / 0",
        python_error="ZeroDivisionError"
    )
    
    formatted = error.format()
    
    assert "ERREUR MEOWLANG [E500]" in formatted
    assert "test.miaou" in formatted
    assert "Ligne        : 10" in formatted
    assert "Colonne      : 5" in formatted
    assert "10 / 0" in formatted
    assert "ZeroDivisionError" in formatted
    assert "croquettes" in formatted.lower()
    assert "Le chat te surveille" in formatted


def test_error_formatting_with_context():
    """Test le formatage avec contexte de code."""
    source_lines = [
        "miaou",
        "nombre = 0",
        "resultat = 10 / nombre",
        "ecrire resultat",
        "meow"
    ]
    
    error_def = ErrorCatalog.get("E500")
    context = extract_context(source_lines, 3)
    
    error = MeowLangError(
        error_def=error_def,
        file="test.miaou",
        line=3,
        column=12,
        instruction="10 / nombre",
        context_lines=context
    )
    
    formatted = error.format()
    
    assert "Contexte :" in formatted
    assert "nombre = 0" in formatted
    assert "resultat = 10 / nombre" in formatted
    assert ">" in formatted


def test_extract_context():
    """Test l'extraction du contexte autour d'une ligne."""
    source_lines = [
        "ligne 1",
        "ligne 2",
        "ligne 3 erreur",
        "ligne 4",
        "ligne 5"
    ]
    
    context = extract_context(source_lines, 3, context_size=1)
    
    assert len(context) == 3
    assert context[0] == (2, "ligne 2", False)
    assert context[1] == (3, "ligne 3 erreur", True)
    assert context[2] == (4, "ligne 4", False)


def test_extract_context_at_start():
    """Test l'extraction du contexte au début du fichier."""
    source_lines = ["ligne 1", "ligne 2", "ligne 3"]
    
    context = extract_context(source_lines, 1, context_size=2)
    
    assert len(context) == 3
    assert context[0] == (1, "ligne 1", True)
    assert context[1] == (2, "ligne 2", False)


def test_extract_context_at_end():
    """Test l'extraction du contexte à la fin du fichier."""
    source_lines = ["ligne 1", "ligne 2", "ligne 3"]
    
    context = extract_context(source_lines, 3, context_size=2)
    
    assert len(context) == 3
    assert context[-1] == (3, "ligne 3", True)


def test_error_with_variables():
    """Test les erreurs avec variables substituées."""
    error_def = ErrorCatalog.get("E200")
    
    error = MeowLangError(
        error_def=error_def,
        file="test.miaou",
        line=5,
        column=1,
        instruction="ecrire x",
        var_name="x"
    )
    
    formatted = error.format()
    
    assert "'x'" in formatted or "x" in formatted


def test_error_severity_emoji():
    """Test que les emojis de sévérité sont corrects."""
    error_faible = ErrorCatalog.get("E602")
    assert error_faible.severity == ErrorSeverity.FAIBLE
    
    error_moyenne = ErrorCatalog.get("E500")
    assert error_moyenne.severity == ErrorSeverity.MOYENNE
    
    error_forte = ErrorCatalog.get("E000")
    assert error_forte.severity == ErrorSeverity.FORTE


def test_division_by_zero_error():
    """Test spécifique pour l'erreur de division par zéro."""
    source_lines = [
        "miaou",
        "nombre = demander nombre \"Donne un nombre :\"",
        "resultat = 10 / nombre",
        "ecrire \"Résultat : \" resultat",
        "meow"
    ]
    
    try:
        ErrorCatalog.raise_error(
            "E500",
            file="aventure_du_chat.miaou",
            line=3,
            column=12,
            instruction="10 / nombre",
            source_lines=source_lines,
            python_error="ZeroDivisionError"
        )
        assert False, "Devrait lever une exception"
    except MeowLangError as e:
        formatted = str(e)
        assert "E500" in formatted
        assert "croquettes" in formatted.lower()
        assert "nombre != 0" in formatted


def test_undefined_variable_error():
    """Test pour variable non définie."""
    try:
        ErrorCatalog.raise_error(
            "E200",
            file="test.miaou",
            line=2,
            column=1,
            instruction="ecrire x",
            var_name="x"
        )
        assert False, "Devrait lever une exception"
    except MeowLangError as e:
        formatted = str(e)
        assert "E200" in formatted
        assert "n'existe pas" in formatted


def test_function_not_found_error():
    """Test pour fonction inconnue."""
    try:
        ErrorCatalog.raise_error(
            "E600",
            file="test.miaou",
            line=3,
            column=1,
            instruction="faire_magie()",
            func_name="faire_magie"
        )
        assert False, "Devrait lever une exception"
    except MeowLangError as e:
        formatted = str(e)
        assert "E600" in formatted
        assert "faire_magie" in formatted
        assert "n'existe pas" in formatted


def test_wrong_number_of_arguments():
    """Test pour mauvais nombre d'arguments."""
    try:
        ErrorCatalog.raise_error(
            "E601",
            file="test.miaou",
            line=4,
            column=1,
            instruction="saluer()",
            expected=1,
            received=0
        )
        assert False, "Devrait lever une exception"
    except MeowLangError as e:
        formatted = str(e)
        assert "E601" in formatted
        assert "caresse" in formatted.lower()


def test_index_out_of_bounds():
    """Test pour index hors limites."""
    try:
        ErrorCatalog.raise_error(
            "E700",
            file="test.miaou",
            line=5,
            column=10,
            instruction="chats[5]",
            index=5,
            size=3,
            size_minus_one=2
        )
        assert False, "Devrait lever une exception"
    except MeowLangError as e:
        formatted = str(e)
        assert "E700" in formatted
        assert "5" in formatted
        assert "portée" in formatted


def test_file_not_found_error():
    """Test pour fichier introuvable."""
    try:
        ErrorCatalog.raise_error(
            "E900",
            file="<import>",
            line=1,
            column=1,
            instruction="importer inexistant",
            filename="inexistant.miaou"
        )
        assert False, "Devrait lever une exception"
    except MeowLangError as e:
        formatted = str(e)
        assert "E900" in formatted
        assert "inexistant.miaou" in formatted


def test_cat_on_keyboard_error():
    """Test pour l'easter egg E999."""
    error_def = ErrorCatalog.get("E999")
    
    assert error_def is not None
    assert "clavier" in error_def.message_meow.lower()
    assert "chat" in error_def.message_meow.lower()
    assert error_def.severity == ErrorSeverity.FORTE


def test_all_error_codes_have_required_fields():
    """Vérifie que toutes les erreurs enregistrées ont les champs requis."""
    all_codes = [
        "E000", "E001", "E002", "E003", "E004",
        "E100", "E101", "E102", "E103", "E104",
        "E200", "E201", "E202", "E203",
        "E300", "E301", "E302",
        "E400", "E401", "E402",
        "E500", "E501", "E502",
        "E600", "E601", "E602",
        "E700", "E701",
        "E800",
        "E900", "E901", "E902", "E999"
    ]
    
    for code in all_codes:
        error_def = ErrorCatalog.get(code)
        assert error_def is not None, f"Code {code} manquant"
        assert error_def.code == code
        assert error_def.name
        assert error_def.message_tech
        assert error_def.message_meow
        assert error_def.severity in [ErrorSeverity.FAIBLE, ErrorSeverity.MOYENNE, ErrorSeverity.FORTE]
        assert error_def.mood
        assert "🐱" in error_def.message_meow or "😾" in error_def.message_meow or "😿" in error_def.message_meow or "🐾" in error_def.message_meow or "😼" in error_def.message_meow or "🧶" in error_def.message_meow or "🐈" in error_def.message_meow or "🤨" in error_def.message_meow or "🚫" in error_def.message_meow or "🐟" in error_def.message_meow or "😵" in error_def.message_meow or "🚪" in error_def.message_meow or "💥" in error_def.message_meow or "💤" in error_def.message_meow or "🪟" in error_def.message_meow or "🧐" in error_def.message_meow or "🙀" in error_def.message_meow or "🕰️" in error_def.message_meow or "👋" in error_def.message_meow


def test_error_message_contains_emojis():
    """Vérifie que les messages d'erreur contiennent bien des emojis."""
    error_def = ErrorCatalog.get("E500")
    error = MeowLangError(
        error_def=error_def,
        file="test.miaou",
        line=1,
        column=1
    )
    
    formatted = error.format()
    
    emoji_count = sum(1 for char in formatted if ord(char) > 0x1F300)
    assert emoji_count > 0, "Le message devrait contenir des emojis"
