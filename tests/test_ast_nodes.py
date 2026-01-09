"""
Tests pour les nœuds AST de MeowLang.
"""

import pytest
from meowlang.ast_nodes import *


class TestPosition:
    def test_position_creation(self):
        pos = Position(10, 5)
        assert pos.line == 10
        assert pos.column == 5
    
    def test_position_str(self):
        pos = Position(10, 5)
        assert str(pos) == "10:5"
    
    def test_create_position_helper(self):
        pos = create_position(20, 15)
        assert pos.line == 20
        assert pos.column == 15


class TestLiterals:
    def test_number_literal(self):
        pos = Position(1, 1)
        lit = Literal(position=pos, value=42, literal_type="number")
        assert lit.value == 42
        assert lit.literal_type == "number"
        assert lit.position == pos
    
    def test_string_literal(self):
        pos = Position(2, 3)
        lit = Literal(position=pos, value="Hello", literal_type="string")
        assert lit.value == "Hello"
        assert lit.literal_type == "string"
    
    def test_boolean_literal(self):
        pos = Position(3, 4)
        lit = Literal(position=pos, value=True, literal_type="boolean")
        assert lit.value is True
        assert lit.literal_type == "boolean"
    
    def test_create_literal_helper(self):
        pos = Position(1, 1)
        lit = create_literal(3.14, "number", pos)
        assert lit.value == 3.14
        assert lit.literal_type == "number"


class TestIdentifiers:
    def test_identifier_creation(self):
        pos = Position(1, 1)
        ident = Identifier(position=pos, name="nom")
        assert ident.name == "nom"
        assert ident.position == pos
    
    def test_create_identifier_helper(self):
        pos = Position(2, 2)
        ident = create_identifier("variable", pos)
        assert ident.name == "variable"


class TestExpressions:
    def test_binary_op(self):
        pos = Position(1, 1)
        left = Literal(position=pos, value=5, literal_type="number")
        right = Literal(position=pos, value=3, literal_type="number")
        binop = BinaryOp(position=pos, left=left, operator="+", right=right)
        
        assert binop.operator == "+"
        assert binop.left == left
        assert binop.right == right
    
    def test_unary_op(self):
        pos = Position(1, 1)
        operand = Identifier(position=pos, name="x")
        unop = UnaryOp(position=pos, operator="non", operand=operand)
        
        assert unop.operator == "non"
        assert unop.operand == operand
    
    def test_function_call_no_args(self):
        pos = Position(1, 1)
        call = FunctionCall(position=pos, name="miauler")
        
        assert call.name == "miauler"
        assert len(call.arguments) == 0
    
    def test_function_call_with_args(self):
        pos = Position(1, 1)
        arg1 = Literal(position=pos, value="Axel", literal_type="string")
        arg2 = Literal(position=pos, value=25, literal_type="number")
        call = FunctionCall(position=pos, name="saluer", arguments=[arg1, arg2])
        
        assert call.name == "saluer"
        assert len(call.arguments) == 2
        assert call.arguments[0] == arg1


class TestStatements:
    def test_assignment(self):
        pos = Position(1, 1)
        value = Literal(position=pos, value=10, literal_type="number")
        assign = Assignment(position=pos, name="x", value=value)
        
        assert assign.name == "x"
        assert assign.value == value
    
    def test_expression_statement(self):
        pos = Position(1, 1)
        call = FunctionCall(position=pos, name="ecrire", arguments=[])
        expr_stmt = ExpressionStatement(position=pos, expression=call)
        
        assert expr_stmt.expression == call
    
    def test_return_with_value(self):
        pos = Position(1, 1)
        value = Literal(position=pos, value=42, literal_type="number")
        ret = ReturnStatement(position=pos, value=value)
        
        assert ret.value == value
    
    def test_return_without_value(self):
        pos = Position(1, 1)
        ret = ReturnStatement(position=pos)
        
        assert ret.value is None


class TestControlFlow:
    def test_if_statement_simple(self):
        pos = Position(1, 1)
        condition = Literal(position=pos, value=True, literal_type="boolean")
        then_block = [Assignment(position=pos, name="x", value=Literal(position=pos, value=1, literal_type="number"))]
        
        if_stmt = IfStatement(position=pos, condition=condition, then_block=then_block)
        
        assert if_stmt.condition == condition
        assert len(if_stmt.then_block) == 1
        assert len(if_stmt.elif_blocks) == 0
        assert if_stmt.else_block is None
    
    def test_if_statement_with_elif(self):
        pos = Position(1, 1)
        condition1 = Literal(position=pos, value=True, literal_type="boolean")
        condition2 = Literal(position=pos, value=False, literal_type="boolean")
        then_block = []
        elif_block = []
        
        if_stmt = IfStatement(
            position=pos,
            condition=condition1,
            then_block=then_block,
            elif_blocks=[(condition2, elif_block)]
        )
        
        assert len(if_stmt.elif_blocks) == 1
        assert if_stmt.elif_blocks[0][0] == condition2
    
    def test_if_statement_with_else(self):
        pos = Position(1, 1)
        condition = Literal(position=pos, value=True, literal_type="boolean")
        then_block = []
        else_block = []
        
        if_stmt = IfStatement(
            position=pos,
            condition=condition,
            then_block=then_block,
            else_block=else_block
        )
        
        assert if_stmt.else_block is not None
        assert len(if_stmt.else_block) == 0
    
    def test_while_loop(self):
        pos = Position(1, 1)
        condition = Literal(position=pos, value=True, literal_type="boolean")
        body = []
        
        while_loop = WhileLoop(position=pos, condition=condition, body=body)
        
        assert while_loop.condition == condition
        assert len(while_loop.body) == 0
    
    def test_repeat_loop(self):
        pos = Position(1, 1)
        count = Literal(position=pos, value=5, literal_type="number")
        body = []
        
        repeat_loop = RepeatLoop(position=pos, count=count, body=body)
        
        assert repeat_loop.count == count
        assert len(repeat_loop.body) == 0
    
    def test_foreach_loop(self):
        pos = Position(1, 1)
        iterable = Identifier(position=pos, name="chats")
        body = []
        
        foreach = ForEachLoop(position=pos, iterator="chat", iterable=iterable, body=body)
        
        assert foreach.iterator == "chat"
        assert foreach.iterable == iterable
        assert len(foreach.body) == 0


class TestFunctions:
    def test_function_def_no_params(self):
        pos = Position(1, 1)
        body = []
        
        func = FunctionDef(position=pos, name="miauler", body=body)
        
        assert func.name == "miauler"
        assert len(func.parameters) == 0
        assert len(func.body) == 0
    
    def test_function_def_with_params(self):
        pos = Position(1, 1)
        body = []
        
        func = FunctionDef(position=pos, name="saluer", parameters=["nom", "age"], body=body)
        
        assert func.name == "saluer"
        assert len(func.parameters) == 2
        assert func.parameters[0] == "nom"
        assert func.parameters[1] == "age"


class TestCollections:
    def test_list_node_empty(self):
        pos = Position(1, 1)
        lst = ListNode(position=pos)
        
        assert len(lst.elements) == 0
    
    def test_list_node_with_elements(self):
        pos = Position(1, 1)
        elem1 = Literal(position=pos, value=1, literal_type="number")
        elem2 = Literal(position=pos, value=2, literal_type="number")
        lst = ListNode(position=pos, elements=[elem1, elem2])
        
        assert len(lst.elements) == 2
        assert lst.elements[0] == elem1
    
    def test_dict_node_empty(self):
        pos = Position(1, 1)
        dct = DictNode(position=pos)
        
        assert len(dct.pairs) == 0
    
    def test_dict_node_with_pairs(self):
        pos = Position(1, 1)
        key = Literal(position=pos, value="nom", literal_type="string")
        value = Literal(position=pos, value="Minou", literal_type="string")
        dct = DictNode(position=pos, pairs=[(key, value)])
        
        assert len(dct.pairs) == 1
        assert dct.pairs[0][0] == key
        assert dct.pairs[0][1] == value
    
    def test_index_access(self):
        pos = Position(1, 1)
        obj = Identifier(position=pos, name="liste")
        index = Literal(position=pos, value=0, literal_type="number")
        access = IndexAccess(position=pos, object=obj, index=index)
        
        assert access.object == obj
        assert access.index == index
    
    def test_index_assignment(self):
        pos = Position(1, 1)
        obj = Identifier(position=pos, name="liste")
        index = Literal(position=pos, value=0, literal_type="number")
        value = Literal(position=pos, value=42, literal_type="number")
        assign = IndexAssignment(position=pos, object=obj, index=index, value=value)
        
        assert assign.object == obj
        assert assign.index == index
        assert assign.value == value


class TestExceptionHandling:
    def test_try_except(self):
        pos = Position(1, 1)
        try_block = []
        except_block = []
        
        try_exc = TryExcept(position=pos, try_block=try_block, except_block=except_block)
        
        assert len(try_exc.try_block) == 0
        assert len(try_exc.except_block) == 0


class TestModules:
    def test_import_statement(self):
        pos = Position(1, 1)
        import_stmt = ImportStatement(position=pos, module_name="math")
        
        assert import_stmt.module_name == "math"
    
    def test_attribute_access(self):
        pos = Position(1, 1)
        obj = Identifier(position=pos, name="math")
        attr = AttributeAccess(position=pos, object=obj, attribute="sqrt")
        
        assert attr.object == obj
        assert attr.attribute == "sqrt"


class TestLoopControl:
    def test_break_statement(self):
        pos = Position(1, 1)
        brk = BreakStatement(position=pos)
        
        assert isinstance(brk, BreakStatement)
    
    def test_continue_statement(self):
        pos = Position(1, 1)
        cont = ContinueStatement(position=pos)
        
        assert isinstance(cont, ContinueStatement)
    
    def test_pass_statement(self):
        pos = Position(1, 1)
        pass_stmt = PassStatement(position=pos)
        
        assert isinstance(pass_stmt, PassStatement)


class TestProgram:
    def test_empty_program(self):
        pos = Position(1, 1)
        prog = Program(position=pos)
        
        assert len(prog.statements) == 0
    
    def test_program_with_statements(self):
        pos = Position(1, 1)
        stmt1 = Assignment(position=pos, name="x", value=Literal(position=pos, value=1, literal_type="number"))
        stmt2 = Assignment(position=pos, name="y", value=Literal(position=pos, value=2, literal_type="number"))
        prog = Program(position=pos, statements=[stmt1, stmt2])
        
        assert len(prog.statements) == 2
        assert prog.statements[0] == stmt1
        assert prog.statements[1] == stmt2


class TestComplexAST:
    def test_nested_binary_operations(self):
        """Test création d'AST pour: (5 + 3) * 2"""
        pos = Position(1, 1)
        
        lit5 = Literal(position=pos, value=5, literal_type="number")
        lit3 = Literal(position=pos, value=3, literal_type="number")
        lit2 = Literal(position=pos, value=2, literal_type="number")
        
        add_op = BinaryOp(position=pos, left=lit5, operator="+", right=lit3)
        mul_op = BinaryOp(position=pos, left=add_op, operator="*", right=lit2)
        
        assert isinstance(mul_op.left, BinaryOp)
        assert mul_op.left.operator == "+"
        assert mul_op.operator == "*"
    
    def test_function_with_body(self):
        """Test création d'une fonction complète"""
        pos = Position(1, 1)
        
        param_x = "x"
        body_return = ReturnStatement(
            position=pos,
            value=BinaryOp(
                position=pos,
                left=Identifier(position=pos, name="x"),
                operator="*",
                right=Literal(position=pos, value=2, literal_type="number")
            )
        )
        
        func = FunctionDef(
            position=pos,
            name="doubler",
            parameters=[param_x],
            body=[body_return]
        )
        
        assert func.name == "doubler"
        assert len(func.parameters) == 1
        assert len(func.body) == 1
        assert isinstance(func.body[0], ReturnStatement)
