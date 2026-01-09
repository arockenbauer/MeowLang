# Spec and build

## Configuration
- **Artifacts Path**: {@artifacts_path} → `.zenflow/tasks/{task_id}`

---

## Agent Instructions

Ask the user questions when anything is unclear or needs their input. This includes:
- Ambiguous or incomplete requirements
- Technical decisions that affect architecture or user experience
- Trade-offs that require business context

Do not make assumptions on important decisions — get clarification first.

---

## Workflow Steps

### [x] Step: Technical Specification

✅ Spécification technique créée dans `spec.md`
- Complexité évaluée: **HARD**
- Architecture définie: Lexer → Parser → AST → Interpreter
- Système d'erreurs avec codes E000-E999
- 9 modules Python à créer

---

### [x] Step: Project Structure & Setup
<!-- chat-id: 9a87cfb2-4983-4d7c-9f17-186da789f29c -->

✅ Structure de base du projet créée
- Arborescence: `meowlang/`, `examples/`, `tests/`
- `setup.py` avec entry point CLI
- `.gitignore` pour Python
- `requirements-dev.txt` (pytest, black, flake8, mypy)
- Fichiers `__init__.py` créés
- Installation `pip install -e .` validée

---

### [x] Step: Error System Implementation
<!-- chat-id: 81ac3f06-b4d1-4e70-b4b9-8e6fa983fbc6 -->

✅ Système d'erreurs MeowLang implémenté et testé

**Fichiers créés:**
- `meowlang/errors.py` : Classes d'erreurs et catalogue complet
- `tests/test_errors.py` : Suite de tests complète

**Tâches accomplies:**
1. ✅ Classe `MeowLangError` avec formatage personnalisé riche
2. ✅ `ErrorCatalog` avec 30+ codes d'erreur (E000-E999)
3. ✅ Méthode `format()` pour affichage avec emojis félins
4. ✅ Fonction `extract_context()` pour extraction de lignes de code

**Vérification:**
- ✅ 17 tests passent avec succès
- ✅ Formatage E500 produit le format attendu avec emojis
- ✅ Extraction de contexte fonctionne correctement
- ✅ Tous les codes d'erreur critiques enregistrés

---

### [x] Step: Lexer Implementation
<!-- chat-id: 368c629a-e4d0-4ac5-ab7d-fac08d569d6d -->

✅ Lexer implémenté et testé avec succès

**Fichiers créés:**
- `meowlang/lexer.py` : Lexer complet avec TokenType enum, Token class et Lexer class
- `tests/test_lexer.py` : Suite de 35 tests
- `examples/hello.miaou` : Exemple de script simple

**Tâches accomplies:**
1. ✅ Tous les tokens définis (MIAOU, MEOW, mots-clés, opérateurs, etc.)
2. ✅ Détection d'indentation (INDENT/DEDENT) comme Python
3. ✅ Reconnaissance de strings (avec échappements), numbers, identifiers
4. ✅ Gestion des commentaires (#)
5. ✅ Tracking précis de position (ligne, colonne) pour chaque token
6. ✅ Support des mots-clés composés (sinon si, tant que, pour chaque)
7. ✅ Case-insensitive keywords
8. ✅ Gestion d'erreurs avec codes E101, E103

**Vérification:**
- ✅ 35/35 tests passent
- ✅ Tokenisation correcte de scripts complexes
- ✅ Indentation multi-niveaux fonctionnelle
- ✅ Position (ligne:colonne) correcte pour tous les tokens
- ✅ Démonstration sur `examples/hello.miaou` réussie

---

### [x] Step: AST Nodes Definition
<!-- chat-id: 9429f300-0a2f-4d1d-96a9-cc0c5717dde1 -->

✅ Toutes les classes de nœuds AST implémentées et testées

**Fichiers créés:**
- `meowlang/ast_nodes.py` : Définitions complètes de tous les nœuds AST
- `tests/test_ast_nodes.py` : Suite de tests complète

**Tâches accomplies:**
1. ✅ Classe de base `ASTNode` avec `Position` (ligne, colonne)
2. ✅ Nœuds pour expressions : `BinaryOp`, `UnaryOp`, `Literal`, `Identifier`, `FunctionCall`, `IndexAccess`, `AttributeAccess`
3. ✅ Nœuds pour statements : `Assignment`, `ExpressionStatement`, `ReturnStatement`, `BreakStatement`, `ContinueStatement`, `PassStatement`
4. ✅ Nœuds pour contrôle de flux : `IfStatement`, `WhileLoop`, `RepeatLoop`, `ForEachLoop`
5. ✅ Nœuds pour fonctions : `FunctionDef`, `FunctionCall`, `ReturnStatement`
6. ✅ Nœuds pour collections : `ListNode`, `DictNode`, `IndexAccess`, `IndexAssignment`
7. ✅ Nœuds pour gestion d'erreurs : `TryExcept`
8. ✅ Nœuds pour modules : `ImportStatement`, `AttributeAccess`
9. ✅ Nœud racine : `Program`

**Vérification:**
- ✅ 41/41 tests passent avec succès
- ✅ Toutes les classes ont attribut `position`
- ✅ Structure permet de représenter tout le langage MeowLang
- ✅ Helpers disponibles (`create_position`, `create_literal`, `create_identifier`)
- ✅ Utilisation de dataclasses pour simplicité et clarté

---

### [x] Step: Parser Implementation
<!-- chat-id: ffc5c440-1ac8-4168-a0bf-491428aedd02 -->

✅ Parser implémenté et testé avec succès

**Fichiers créés:**
- `meowlang/parser.py` : Parser récursif descendant complet
- `tests/test_parser.py` : Suite de 37 tests

**Tâches accomplies:**
1. ✅ Recursive Descent Parser implémenté
2. ✅ Parsing d'expressions avec priorité d'opérateurs correcte
3. ✅ Parsing de tous les statements (assignment, if, while, repeat, foreach, etc.)
4. ✅ Parsing de définitions de fonctions avec paramètres
5. ✅ Parsing de try/except et imports
6. ✅ Gestion d'erreurs de syntaxe (E100-E199, E102-E104)
7. ✅ Support de `ecrire` avec arguments multiples
8. ✅ Support de `demander texte/nombre`
9. ✅ Support de `aleatoire min a max`
10. ✅ Support des fonctions built-in (minuscule, sqrt, etc.)
11. ✅ Support d'accès aux attributs (module.fonction)
12. ✅ Support d'indexation et assignation par index
13. ✅ Gestion du token DOT pour accès aux attributs
14. ✅ Modifications du lexer pour éviter conflits (a, texte, nombre comme identifiants)

**Vérification:**
- ✅ 37/37 tests du parser passent
- ✅ 130/130 tests totaux passent (lexer + ast + errors + parser)
- ✅ Parser produit AST valide pour scripts complexes
- ✅ Erreurs de syntaxe génèrent codes d'erreur appropriés
- ✅ Priorité d'opérateurs correcte (puissance, mult/div, add/sub, comparaison, logique)
- ✅ Support complet des blocs indentés (INDENT/DEDENT)
- ✅ Gestion correcte des expressions imbriquées et parenthésées

---

### [ ] Step: Type System & Built-in Types
<!-- chat-id: 0e242549-8d7f-4975-94d7-8d0f8d2846e2 -->

Implémenter les types de données MeowLang.

**Fichiers:**
- `meowlang/types.py`

**Tâches:**
1. Wrapper classes: `MeowString`, `MeowNumber`, `MeowBoolean`
2. Collections: `MeowList`, `MeowDict`
3. `MeowFunction` (closure support)
4. `MeowFile` (gestion fichiers)
5. `MeowModule` (système de modules)
6. Fonctions de conversion (`to_meow_bool`, etc.)

**Vérification:**
- Conversions de types fonctionnent
- Collections supportent opérations standard

---

### [ ] Step: Built-in Functions

Implémenter toutes les fonctions built-in.

**Fichiers:**
- `meowlang/builtins.py`

**Tâches:**
1. I/O: `ecrire`, `demander_texte`, `demander_nombre`
2. Strings: `minuscule`, `majuscule`, `longueur`, `remplacer`, `contient`
3. Maths: `aleatoire`, `sqrt`, `abs`, `round`, `floor`, `ceil`
4. Collections: `liste`, `dictionnaire`
5. Fichiers: `ouvrir`, `lire`, `fermer`
6. Système: `attendre`

**Vérification:**
- Chaque fonction built-in testée individuellement
- Gestion d'erreurs appropriée (E500-E599, E800-E899)

---

### [ ] Step: Interpreter Core

Implémenter l'interpréteur principal.

**Fichiers:**
- `meowlang/interpreter.py`

**Tâches:**
1. Créer classe `Environment` (scope management)
2. Créer classe `Interpreter` avec méthode `visit()`
3. Implémenter visiteurs pour expressions
4. Implémenter visiteurs pour statements
5. Implémenter exécution de fonctions
6. Gérer variable spéciale `compteur` dans boucles

**Vérification:**
- Exécuter script simple avec variables, calculs
- Scopes fonctionnent correctement
- Tests: `tests/test_interpreter.py`

---

### [ ] Step: Control Flow & Loops

Implémenter conditions et boucles dans l'interpréteur.

**Tâches:**
1. Exécution `si/sinon/sinon si`
2. Exécution `tant que`
3. Exécution `repeter N fois` avec `compteur`
4. Exécution `pour chaque ... dans`
5. Support `break`/`continue` (si souhaité)

**Vérification:**
- Conditions imbriquées fonctionnent
- Boucles while et for exécutent correctement
- Variable `compteur` accessible

---

### [ ] Step: Functions & Module System

Implémenter fonctions utilisateur et imports.

**Tâches:**
1. Définition et appel de fonctions
2. Closures (capture de variables)
3. Système de résolution de modules
4. Cache de modules
5. Import et exécution de modules

**Vérification:**
- Fonctions avec paramètres fonctionnent
- Closures capturent bonnes variables
- `importer` charge et exécute module
- Tests avec module séparé

---

### [ ] Step: Exception Handling

Implémenter `essayer/sauf erreur`.

**Tâches:**
1. Propagation d'erreurs dans l'interpréteur
2. Capture d'erreurs avec `essayer/sauf`
3. Variable `erreur` dans bloc sauf

**Vérification:**
- Division par zéro catchée
- Autres erreurs runtime catchées
- Erreurs non catchées affichent bon format

---

### [ ] Step: CLI Interface

Créer l'interface en ligne de commande.

**Fichiers:**
- `meowlang/cli.py`

**Tâches:**
1. Argparse pour options (`--help`, `--version`, `--debug`)
2. Exécution de fichier .miaou
3. REPL interactif avec prompt `🐱> `
4. Affichage d'erreurs formatées
5. Mode debug (affiche AST)

**Vérification:**
- `meowlang script.miaou` exécute
- REPL fonctionne
- Erreurs affichées avec bon format

---

### [ ] Step: Example Scripts

Créer les scripts d'exemple.

**Fichiers:**
- `examples/hello.miaou`
- `examples/aventure_du_chat.miaou`
- `examples/tests_complets.miaou`

**Tâches:**
1. Script hello world simple
2. Script aventure du chat (fourni par utilisateur)
3. Script de test complet (tous les features)

**Vérification:**
- Tous les exemples s'exécutent sans erreur
- Comportement attendu confirmé

---

### [ ] Step: Comprehensive Testing

Créer suite de tests complète.

**Fichiers:**
- `tests/test_lexer.py`
- `tests/test_parser.py`
- `tests/test_interpreter.py`
- `tests/test_errors.py`
- `tests/test_builtins.py`

**Tâches:**
1. Tests unitaires pour chaque composant
2. Tests d'intégration end-to-end
3. Tests de cas d'erreur
4. Coverage > 80%

**Vérification:**
- `pytest tests/` passe tous les tests
- Coverage acceptable

---

### [ ] Step: Documentation & Polish

Finaliser documentation et polish.

**Fichiers:**
- `README.md`

**Tâches:**
1. README avec introduction, installation, usage
2. Exemples de code dans README
3. Documentation des erreurs
4. Vérifier emojis affichent bien sur Windows/Linux/Mac

**Vérification:**
- README clair et complet
- Installation via pip fonctionne
- Emojis affichent correctement

---

### [ ] Step: Final Verification & Report

Tests finaux et rapport.

**Tâches:**
1. Exécuter tous les exemples
2. Vérifier toutes les fonctions built-in
3. Tester système d'erreurs complet
4. Rédiger rapport final dans `report.md`

**Vérification:**
- Tous les objectifs du spec atteints
- Rapport documente implémentation et challenges

**Rapport (`{@artifacts_path}/report.md`):**
- Ce qui a été implémenté
- Comment la solution a été testée
- Principaux défis rencontrés
- Limitations connues
