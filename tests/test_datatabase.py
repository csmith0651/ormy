import pytest

from ormy.datatabase import *
from ormy.query_engine import *
from tests.models_for_testing import AllValueTypes


class TestDatabase:
    def test_compile(self):
        db = Database()
        comp = db.query(AllValueTypes).field('int_col').eq().value(True).compile()
        # merely check that the query was converted into an AST
        assert issubclass(type(comp), Expr)
        assert comp.left is not None
        assert comp.left.left is not None
        assert comp.left.right is not None

    # NOTE: don't test eval in the Database class since that requires a concrete platform specific Database child class.

    def test_query(self):
        db = Database()
        query = db.query(AllValueTypes).field('float_col').eq().value(True)
        while query is not None:
            assert issubclass(type(query), CodeQueryBase)
            query = query.child

    def test_convert_query_to_expr_tree_no_ops(self):
        expr_tree = Database().query(AllValueTypes).compile()
        # todo: figure out way to make failure print out the string description of the two trees instead of the objects
        assert expr_tree == QueryExpr(AllValueTypes).children(ValueExpr(True))

    def test_convert_query_to_expr_tree_simple_filter(self):
        expr_tree = Database().query(AllValueTypes).field('int_col').eq().value(100).compile()
        assert expr_tree == QueryExpr(AllValueTypes).children(EqExpr().children(FieldExpr('int_col'), ValueExpr(100)))

    def test_convert_query_and(self):
        expr_tree = Database().query(AllValueTypes).field('int_col').eq().value(100).AND().field('string_col')\
            .eq().value(200).compile()
        assert expr_tree == QueryExpr(AllValueTypes).children(AndExpr().children(
            EqExpr().children(FieldExpr('int_col'), ValueExpr(100)),
            EqExpr().children(FieldExpr('string_col'), ValueExpr(200))))

    def test_bad_field_name(self):
        with pytest.raises(DatabaseException) as error:
            Database().query(AllValueTypes).field('bad_field_name')
        assert "field 'bad_field_name' does not exist in model 'AllValueTypes'" in str(error.value)
