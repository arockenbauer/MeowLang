# MeowLang - Spécification Technique

## Évaluation de la complexité

**Difficulté : HARD**

Créer un langage de programmation complet nécessite :
- Un lexer pour tokeniser le code source
- Un parser pour construire un AST (Abstract Syntax Tree)
- Un interpréteur pour exécuter l'AST
- Un système d'erreurs sophistiqué avec codes et messages personnalisés
- Support de multiples types de données (strings, numbers, lists, dictionaries, booleans)
- Gestion de fonctions définies par l'utilisateur
- Système de modules/imports
- Gestion I/O (fichiers, input utilisateur)
- Opérations mathématiques et aléatoires

---

## Contexte Technique

### Langage d'implémentation
**Python 3.8+**

Raisons :
- Excellent pour créer des interpréteurs (voir Python lui-même, Lark, etc.)
- Bibliothèques riches pour parsing
- Manipulation facile des structures de données
- Gestion d'erreurs robuste
- Cross-platform

### Dépendances
- Aucune dépendance externe requise pour la version de base
- Utilisation de modules Python standard uniquement :
  - `re` : expressions régulières pour le lexer
  - `sys` : arguments CLI et gestion système
  - `random` : pour la fonction `aleatoire`
  - `math` : pour fonctions mathématiques (`sqrt`, `abs`, etc.)
  - `os` : pour gestion de fichiers et chemins
  - `pathlib` : manipulation de chemins

### Extensions de fichier
- Scripts MeowLang : `.miaou`
- Modules MeowLang : `.miaou` (identique)

---

## Architecture du Projet

### Structure des fichiers

```
meowlang/
├── meowlang/
│   ├── __init__.py
│   ├── lexer.py           # Tokenisation du code source
│   ├── parser.py          # Construction de l'AST
│   ├── ast_nodes.py       # Définition des nœuds AST
│   ├── interpreter.py     # Exécution de l'AST
│   ├── errors.py          # Système d'erreurs MeowLang
│   ├── builtins.py        # Fonctions built-in (ecrire, demander, etc.)
│   ├── types.py           # Types de données MeowLang
│   └── cli.py             # Interface en ligne de commande
├── examples/
│   ├── hello.miaou
│   ├── aventure_du_chat.miaou
│   └── tests_complets.miaou
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_interpreter.py
│   └── test_errors.py
├── README.md
├── setup.py               # Pour installation pip
└── requirements-dev.txt   # Dépendances de dev (pytest, etc.)
```

---

## Approche d'implémentation

### 1. Lexer (meowlang/lexer.py)

**Responsabilité** : Transformer le code source en tokens

**Tokens principaux** :
- `MIAOU`, `MEOW` : marqueurs de début/fin
- `ECRIRE`, `DEMANDER`, `TEXTE`, `NOMBRE` : I/O
- `SI`, `ALORS`, `SINON`, `SINON_SI` : conditions
- `REPETER`, `FOIS`, `TANT_QUE`, `POUR_CHAQUE`, `DANS` : boucles
- `FONCTION`, `RETOUR` : fonctions
- `LISTE`, `DICTIONNAIRE` : collections
- `ESSAYER`, `SAUF`, `ERREUR` : exceptions
- `IMPORTER` : modules
- `IDENTIFIER` : noms de variables/fonctions
- `STRING`, `NUMBER`, `BOOLEAN` : littéraux
- `OPERATORS` : `+`, `-`, `*`, `/`, `//`, `%`, `**`, `=`, `!=`, `<`, `>`, `<=`, `>=`, `ET`, `OU`, `NON`
- `DELIMITERS` : `:`, `,`, `(`, `)`, `[`, `]`, `"`
- `NEWLINE`, `INDENT`, `DEDENT` : structure (comme Python)
- `COMMENT` : `#` (ignoré)

**Algorithme** :
1. Lire le fichier ligne par ligne
2. Détecter l'indentation (espaces/tabs) → générer INDENT/DEDENT
3. Identifier mots-clés vs identifiers
4. Extraire strings, numbers, operators
5. Retourner liste de tokens avec position (ligne, colonne)

### 2. Parser (meowlang/parser.py)

**Responsabilité** : Construire l'AST à partir des tokens

**Grammaire simplifiée** :
```
program         → MIAOU statements MEOW
statements      → statement*
statement       → expression | assignment | control_flow | function_def | import_stmt
assignment      → IDENTIFIER '=' expression
expression      → term (('+' | '-' | 'ET' | 'OU') term)*
term            → factor (('*' | '/' | '//' | '%' | '**') factor)*
factor          → NUMBER | STRING | BOOLEAN | IDENTIFIER | function_call | list | dict | '(' expression ')'
function_call   → IDENTIFIER '(' arguments? ')'
control_flow    → if_stmt | while_stmt | for_stmt | try_stmt
if_stmt         → 'si' expression 'alors' ':' block ('sinon si' expression 'alors' ':' block)* ('sinon' ':' block)?
while_stmt      → 'tant que' expression ':' block
for_stmt        → 'repeter' NUMBER 'fois' ':' block | 'pour chaque' IDENTIFIER 'dans' expression ':' block
try_stmt        → 'essayer' ':' block 'sauf erreur' ':' block
function_def    → 'fonction' IDENTIFIER '(' parameters? ')' ':' block
block           → INDENT statements DEDENT
```

**Méthode** : Recursive Descent Parser
- Parsing top-down
- Gestion de la priorité des opérateurs
- Construction de nœuds AST typés

### 3. AST Nodes (meowlang/ast_nodes.py)

**Classes de nœuds** :
```python
class ASTNode:
    position: (line, column)

class Program(ASTNode):
    statements: list[Statement]

class Assignment(ASTNode):
    name: str
    value: Expression

class BinaryOp(ASTNode):
    left: Expression
    operator: str
    right: Expression

class FunctionCall(ASTNode):
    name: str
    arguments: list[Expression]

class IfStatement(ASTNode):
    condition: Expression
    then_block: list[Statement]
    elif_blocks: list[(Expression, list[Statement])]
    else_block: list[Statement]

class WhileLoop(ASTNode):
    condition: Expression
    body: list[Statement]

class ForLoop(ASTNode):
    iterator: str | None
    iterable: Expression | int
    body: list[Statement]

class FunctionDef(ASTNode):
    name: str
    parameters: list[str]
    body: list[Statement]

class TryExcept(ASTNode):
    try_block: list[Statement]
    except_block: list[Statement]

class Literal(ASTNode):
    value: any
    type: str  # "string", "number", "boolean"

class Identifier(ASTNode):
    name: str

class ListNode(ASTNode):
    elements: list[Expression]

class DictNode(ASTNode):
    pairs: list[(Expression, Expression)]
```

### 4. Interpréteur (meowlang/interpreter.py)

**Responsabilité** : Exécuter l'AST

**Environnement d'exécution** :
```python
class Environment:
    variables: dict[str, any]
    parent: Environment | None
    
    def get(name: str) → any
    def set(name: str, value: any)
    def define(name: str, value: any)

class Interpreter:
    global_env: Environment
    current_env: Environment
    
    def visit(node: ASTNode) → any
    def visit_Program(node: Program)
    def visit_Assignment(node: Assignment)
    def visit_BinaryOp(node: BinaryOp)
    # ... pour chaque type de nœud
```

**Gestion des scopes** :
- Scope global pour variables globales et fonctions
- Nouveau scope pour chaque fonction appelée
- Nouveau scope pour boucles (accès `compteur`)

**Fonctions built-in** (dans `builtins.py`) :
- `ecrire(*args)` : print
- `demander_texte(prompt)` : input string
- `demander_nombre(prompt)` : input number avec validation
- `minuscule(s)` : lower()
- `majuscule(s)` : upper()
- `longueur(obj)` : len()
- `liste(*args)` : create list
- `dictionnaire(**kwargs)` : create dict
- `aleatoire(min, max)` : random
- `sqrt(n)`, `abs(n)`, `round(n)`, `floor(n)`, `ceil(n)` : math
- `ouvrir(path, mode)` : file open
- `lire(file)` : file read
- `fermer(file)` : file close
- `attendre(seconds)` : time.sleep()

### 5. Système d'erreurs (meowlang/errors.py)

**Classes d'erreurs** :
```python
class MeowLangError(Exception):
    code: str  # E000-E999
    message_tech: str
    message_meow: str
    file: str
    line: int
    column: int
    context: str  # lignes de code autour
    suggestion: str
    
    def format() → str  # Format comme dans l'exemple

class ErrorCatalog:
    errors: dict[str, ErrorDefinition]
    
    @staticmethod
    def get(code: str) → ErrorDefinition
    
    @staticmethod
    def raise_error(code: str, position: tuple, **kwargs)
```

**Catalogue d'erreurs** :
- E000-E099 : Structure
- E100-E199 : Syntaxe
- E200-E299 : Variables
- E300-E399 : Conditions
- E400-E499 : Boucles
- E500-E599 : Maths
- E600-E699 : Fonctions
- E700-E799 : Collections
- E800-E899 : Système
- E900-E999 : Critiques

**Format de sortie d'erreur** :
```
😾 ERREUR MEOWLANG [E###] — GRIFFURE [FAIBLE/MOYENNE/FORTE]

Fichier      : {file}
Ligne        : {line}
Colonne      : {column}
Instruction  : {instruction}

Type         : {type_officiel}
Code interne : {python_error_type}

Message technique :
{message_tech}

Message MeowLang 🐱 :
{message_meow}

Contexte :
  {line-2} | {code}
  {line-1} | {code}
> {line}   | {code}
           {pointer}

État du chat :
{emoji_mood}

Suggestion du chat 💡 :
{suggestion}

Exemple recommandé :
{example_code}

Fin du jugement.
Le chat te surveille.
```

### 6. CLI (meowlang/cli.py)

**Interface** :
```bash
# Exécuter un script
meowlang script.miaou

# REPL interactif
meowlang

# Version
meowlang --version

# Aide
meowlang --help
```

**Fonctionnalités** :
- Charger et exécuter fichier .miaou
- REPL avec prompt `🐱> `
- Affichage erreurs formatées
- Mode debug (`--debug`) pour afficher AST

---

## Modèle de données

### Types de données MeowLang

```python
# Types primitifs
MeowString : str
MeowNumber : int | float
MeowBoolean : bool (vrai/faux)

# Collections
MeowList : list
MeowDict : dict

# Fonctions
MeowFunction:
    name: str
    parameters: list[str]
    body: list[Statement]
    closure_env: Environment

# Fichiers
MeowFile:
    handle: file object
    path: str
    mode: str

# Modules
MeowModule:
    name: str
    path: str
    exports: dict[str, any]
```

### Conversion de types

```python
def to_meow_bool(value) → bool:
    # "" → faux, 0 → faux, [] → faux
    # Tout le reste → vrai

def to_meow_string(value) → str:
    # Conversion standard

def to_meow_number(value) → int | float:
    # Parse ou erreur E203
```

---

## Système de modules

### Import simple
```python
# fichier: math_chats.miaou
fonction doubler(n):
  resultat = n * 2
  ecrire resultat

# fichier: main.miaou
importer math_chats

math_chats.doubler(5)
```

### Résolution de modules
1. Chercher dans le même dossier que le script
2. Chercher dans `MEOWLANG_PATH` (variable d'environnement)
3. Chercher dans dossier stdlib (si on en crée un)
4. Erreur E900 si introuvable

### Cache de modules
- Chaque module n'est parsé/exécuté qu'une fois
- Stocké dans `Interpreter.loaded_modules: dict[str, MeowModule]`

---

## Vérification et Tests

### Structure de tests

```python
# tests/test_lexer.py
def test_tokenize_simple()
def test_tokenize_keywords()
def test_tokenize_strings()
def test_tokenize_numbers()
def test_tokenize_indentation()

# tests/test_parser.py
def test_parse_assignment()
def test_parse_if_statement()
def test_parse_function_def()
def test_parse_loops()

# tests/test_interpreter.py
def test_execute_arithmetic()
def test_execute_conditions()
def test_execute_functions()
def test_execute_loops()
def test_builtin_functions()

# tests/test_errors.py
def test_error_formatting()
def test_division_by_zero()
def test_undefined_variable()
def test_syntax_errors()
```

### Framework de tests
**pytest**

### Commandes de vérification

```bash
# Tests unitaires
pytest tests/

# Tests d'exemples
meowlang examples/hello.miaou
meowlang examples/aventure_du_chat.miaou

# Linting
flake8 meowlang/
black meowlang/ --check

# Type checking
mypy meowlang/
```

### Métriques de réussite
- ✅ Tous les tests unitaires passent
- ✅ Le script d'exemple complet s'exécute sans erreur
- ✅ Les erreurs affichent le bon format avec emoji
- ✅ Toutes les fonctions built-in fonctionnent
- ✅ Le système de modules charge correctement
- ✅ Les scopes de variables sont corrects

---

## Considérations spéciales

### Gestion de l'indentation (comme Python)
- Utiliser un système INDENT/DEDENT comme Python
- Détecter espaces vs tabs (erreur si mixte)
- Stack d'indentation dans le lexer

### Variable spéciale `compteur`
- Accessible dans boucles `repeter N fois:`
- Valeur : 0 à N-1 (ou 1 à N selon préférence utilisateur)
- Automatiquement injectée dans le scope de la boucle

### Emojis dans les erreurs
- Utiliser UTF-8 pour l'affichage
- Tester sur Windows/Linux/Mac
- Fallback si terminal ne supporte pas

### Performance
- Pas d'optimisation pour V1
- Interprétation directe de l'AST
- Optimisations futures possibles : bytecode, JIT

---

## Fichiers créés/modifiés

### Nouveaux fichiers
- `meowlang/__init__.py`
- `meowlang/lexer.py`
- `meowlang/parser.py`
- `meowlang/ast_nodes.py`
- `meowlang/interpreter.py`
- `meowlang/errors.py`
- `meowlang/builtins.py`
- `meowlang/types.py`
- `meowlang/cli.py`
- `examples/hello.miaou`
- `examples/aventure_du_chat.miaou`
- `tests/test_lexer.py`
- `tests/test_parser.py`
- `tests/test_interpreter.py`
- `tests/test_errors.py`
- `setup.py`
- `requirements-dev.txt`
- `README.md`
- `.gitignore`

### Fichiers modifiés
Aucun (nouveau projet)

---

## Installation et utilisation

### Installation
```bash
cd meowlang
pip install -e .
```

### Utilisation
```bash
# Exécuter un script
meowlang examples/hello.miaou

# REPL
meowlang

# Aide
meowlang --help
```

---

## Extensions futures (hors scope V1)

- Debugger interactif
- Compilation en bytecode
- Standard library (module json, http, etc.)
- Package manager (pip pour MeowLang)
- IDE support (syntax highlighting, LSP)
- Optimisations (tail call, constant folding)
- Type hints optionnels
- Compilation vers Python/JS
