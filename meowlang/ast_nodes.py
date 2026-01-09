"""
AST Nodes pour MeowLang - Définition de tous les nœuds de l'arbre syntaxique abstrait.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Tuple


@dataclass
class Position:
    """Position dans le code source (ligne, colonne)."""
    line: int
    column: int
    
    def __str__(self):
        return f"{self.line}:{self.column}"


@dataclass
class ASTNode:
    """Classe de base pour tous les nœuds AST."""
    position: Position
    
    def __repr__(self):
        return f"{self.__class__.__name__}(position={self.position})"


@dataclass
class Program(ASTNode):
    """Programme complet MeowLang (miaou ... meow)."""
    statements: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


@dataclass
class Literal(ASTNode):
    """Littéral (nombre, string, boolean)."""
    value: Any
    literal_type: str
    
    def __repr__(self):
        return f"Literal({self.literal_type}={repr(self.value)})"


@dataclass
class Identifier(ASTNode):
    """Identifiant de variable ou fonction."""
    name: str
    
    def __repr__(self):
        return f"Identifier({self.name})"


@dataclass
class BinaryOp(ASTNode):
    """Opération binaire (a + b, a * b, etc.)."""
    left: ASTNode
    operator: str
    right: ASTNode
    
    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


@dataclass
class UnaryOp(ASTNode):
    """Opération unaire (non x, -x)."""
    operator: str
    operand: ASTNode
    
    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand})"


@dataclass
class Assignment(ASTNode):
    """Assignation de variable (x = 5)."""
    name: str
    value: ASTNode
    
    def __repr__(self):
        return f"Assignment({self.name} = {self.value})"


@dataclass
class FunctionCall(ASTNode):
    """Appel de fonction (saluer("Axel"))."""
    name: str
    arguments: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self):
        return f"FunctionCall({self.name}({len(self.arguments)} args))"


@dataclass
class IfStatement(ASTNode):
    """Instruction conditionnelle (si/sinon si/sinon)."""
    condition: ASTNode
    then_block: List[ASTNode] = field(default_factory=list)
    elif_blocks: List[Tuple[ASTNode, List[ASTNode]]] = field(default_factory=list)
    else_block: Optional[List[ASTNode]] = None
    
    def __repr__(self):
        return f"IfStatement(condition={self.condition}, {len(self.elif_blocks)} elif, else={self.else_block is not None})"


@dataclass
class WhileLoop(ASTNode):
    """Boucle tant que (tant que condition:)."""
    condition: ASTNode
    body: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self):
        return f"WhileLoop(condition={self.condition}, {len(self.body)} statements)"


@dataclass
class RepeatLoop(ASTNode):
    """Boucle répéter N fois (repeter 5 fois:)."""
    count: ASTNode
    body: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self):
        return f"RepeatLoop(count={self.count}, {len(self.body)} statements)"


@dataclass
class ForEachLoop(ASTNode):
    """Boucle pour chaque (pour chaque x dans liste:)."""
    iterator: str
    iterable: ASTNode
    body: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self):
        return f"ForEachLoop({self.iterator} in {self.iterable}, {len(self.body)} statements)"


@dataclass
class FunctionDef(ASTNode):
    """Définition de fonction (fonction saluer(nom):)."""
    name: str
    parameters: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self):
        return f"FunctionDef({self.name}({', '.join(self.parameters)}))"


@dataclass
class ReturnStatement(ASTNode):
    """Instruction retour (retour valeur)."""
    value: Optional[ASTNode] = None
    
    def __repr__(self):
        return f"ReturnStatement({self.value})"


@dataclass
class ListNode(ASTNode):
    """Littéral liste (liste(1, 2, 3))."""
    elements: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self):
        return f"ListNode([{len(self.elements)} elements])"


@dataclass
class DictNode(ASTNode):
    """Littéral dictionnaire (dictionnaire("nom":"Axel", "age":25))."""
    pairs: List[Tuple[ASTNode, ASTNode]] = field(default_factory=list)
    
    def __repr__(self):
        return f"DictNode({{{len(self.pairs)} pairs}})"


@dataclass
class IndexAccess(ASTNode):
    """Accès par index (liste[0], dict["clé"])."""
    object: ASTNode
    index: ASTNode
    
    def __repr__(self):
        return f"IndexAccess({self.object}[{self.index}])"


@dataclass
class IndexAssignment(ASTNode):
    """Assignation par index (liste[0] = 5, dict["clé"] = "valeur")."""
    object: ASTNode
    index: ASTNode
    value: ASTNode
    
    def __repr__(self):
        return f"IndexAssignment({self.object}[{self.index}] = {self.value})"


@dataclass
class TryExcept(ASTNode):
    """Gestion d'erreurs (essayer: ... sauf erreur: ...)."""
    try_block: List[ASTNode] = field(default_factory=list)
    except_block: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self):
        return f"TryExcept({len(self.try_block)} statements, {len(self.except_block)} except)"


@dataclass
class ImportStatement(ASTNode):
    """Import de module (importer nom_module)."""
    module_name: str
    
    def __repr__(self):
        return f"ImportStatement({self.module_name})"


@dataclass
class AttributeAccess(ASTNode):
    """Accès à un attribut (module.fonction)."""
    object: ASTNode
    attribute: str
    
    def __repr__(self):
        return f"AttributeAccess({self.object}.{self.attribute})"


@dataclass
class BreakStatement(ASTNode):
    """Instruction break (sortir de boucle)."""
    
    def __repr__(self):
        return "BreakStatement()"


@dataclass
class ContinueStatement(ASTNode):
    """Instruction continue (continuer boucle)."""
    
    def __repr__(self):
        return "ContinueStatement()"


@dataclass
class PassStatement(ASTNode):
    """Instruction pass (ne rien faire)."""
    
    def __repr__(self):
        return "PassStatement()"


@dataclass
class ExpressionStatement(ASTNode):
    """Statement qui est juste une expression (appel de fonction sans assignation)."""
    expression: ASTNode
    
    def __repr__(self):
        return f"ExpressionStatement({self.expression})"


def create_position(line: int, column: int) -> Position:
    """Helper pour créer une position."""
    return Position(line, column)


def create_literal(value: Any, literal_type: str, position: Position) -> Literal:
    """Helper pour créer un littéral."""
    return Literal(position=position, value=value, literal_type=literal_type)


def create_identifier(name: str, position: Position) -> Identifier:
    """Helper pour créer un identifiant."""
    return Identifier(position=position, name=name)
