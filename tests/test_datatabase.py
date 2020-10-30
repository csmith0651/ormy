import pytest

from ormy.column import *
from ormy.datatabase import *
from ormy.model import Model
from ormy.query_engine import *


class TestModel(Model):
    columns = [
        Column('intcol', IntegerColumnType()),
        Column('floatcol', FloatColumnType()),
        Column('stringcol', StringColumnType()),
    ]


class TestDatabase:
    def test_compile(self):
        db = Database()
        comp = db.query(TestModel).field('intcol').eq().value(True).compile()
        # merely check that the query was converted into an AST
        assert issubclass(type(comp), Expr)
        assert comp.left is not None
        assert comp.left.left is not None
        assert comp.left.right is not None

    # NOTE: don't test eval in the Database class since that requires a concrete platform specific Database child class.

    def test_query(self):
        db = Database()
        query = db.query(TestModel).field('floatcol').eq().value(True)
        while query is not None:
            assert issubclass(type(query), CodeQueryBase)
            query = query.child

    def test_convert_query_to_expr_tree_no_ops(self):
        expr_tree = Database().query(TestModel).compile()
        # todo: figure out way to make failure print out the string description of the two trees instead of the objects
        assert expr_tree == QueryExpr(TestModel).children(ValueExpr(True))

    def test_convert_query_to_expr_tree_simple_filter(self):
        expr_tree = Database().query(TestModel).field('intcol').eq().value(100).compile()
        assert expr_tree == QueryExpr(TestModel).children(EqExpr().children(FieldExpr('intcol'), ValueExpr(100)))

    def test_convert_query_and(self):
        expr_tree = Database().query(TestModel).field('intcol').eq().value(100).AND().field('stringcol').eq().value(200).compile()
        assert expr_tree == QueryExpr(TestModel).children(AndExpr()
                                                          .children(EqExpr().children(FieldExpr('intcol'), ValueExpr(100)),
                                                                    EqExpr().children(FieldExpr('stringcol'), ValueExpr(200))))

    def test_bad_field_name(self):
        with pytest.raises(DatabaseException) as error:
            Database().query(TestModel).field('bad_field_name')
        assert "field 'bad_field_name' does not exist in model 'TestModel'" in str(error.value)
