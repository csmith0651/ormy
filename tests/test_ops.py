import pytest

from ormy.column import *
from ormy.csv_database import CsvDatabase
from ormy.model import Model


class ModelForTest(Model):
    __csv_file__ = "f1.csv"
    __table_name__ = "f1"
    FORMAT_STR = "%Y-%m-%d %H:%M:%S.%f"

    columns = [
        Column('intcol', IntegerColumnType(), tags=['t1', 't2']),
        Column('floatcol', FloatColumnType(), tags=['t2', 't3']),
        Column('stringcol', StringColumnType(), tags=['t4']),
        Column('datecol', DateColumnType(FORMAT_STR)),
    ]


class TestOpNode:
    def test_find_in_parents(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        q = db.query(ModelForTest).where('intcol').eq(50)
        assert q.find_in_parents('model') == (True, ModelForTest)

    def test_find_columns(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        q = db.query(ModelForTest)
        assert q.find_columns(['floatcol']) == [ModelForTest.columns[1]]
        assert q.find_columns(['stringcol']) == [ModelForTest.columns[2]]
        assert q.find_columns(['stringcol', 'intcol']) == [ModelForTest.columns[0], ModelForTest.columns[2]]
        assert q.find_columns(['foobar']) == []


class TestListResultOpNode:
    def test_eq(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        eq = db.query(ModelForTest).where('intcol').eq(50)
        assert eq.perform_comparison(eq.comparison_value, 50) == True
        assert eq.perform_comparison(eq.comparison_value, 49) == False

    def test_lt(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        lt = db.query(ModelForTest).where('intcol').lt(50)
        assert lt.perform_comparison(lt.comparison_value, 51) == True
        assert lt.perform_comparison(lt.comparison_value, 50) == False
        assert lt.perform_comparison(lt.comparison_value, 49) == False

    def test_lte(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        lte = db.query(ModelForTest).where('intcol').lte(50)
        assert lte.perform_comparison(lte.comparison_value, 51) == True
        assert lte.perform_comparison(lte.comparison_value, 50) == True
        assert lte.perform_comparison(lte.comparison_value, 49) == False

    def test_gt(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        gt = db.query(ModelForTest).where('intcol').gt(50)
        assert gt.perform_comparison(gt.comparison_value, 49) == True
        assert gt.perform_comparison(gt.comparison_value, 50) == False
        assert gt.perform_comparison(gt.comparison_value, 51) == False

    def test_gte(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        gte = db.query(ModelForTest).where('intcol').gte(50)
        assert gte.perform_comparison(gte.comparison_value, 49) == True
        assert gte.perform_comparison(gte.comparison_value, 50) == True
        assert gte.perform_comparison(gte.comparison_value, 51) == False


class TestComparisonOp:
    def test_find_where_field(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        eq = db.query(ModelForTest).where('intcol').eq(50)
        assert eq.find_where_fields() == ['intcol']

        eq = db.query(ModelForTest).where_tag('t1').eq(50)
        assert eq.find_where_fields() == ['intcol']

        eq = db.query(ModelForTest).where_tag('t2').eq(50)
        assert eq.find_where_fields() == ['intcol', 'floatcol']

        eq = db.query(ModelForTest).where_tag('t3').eq(50)
        assert eq.find_where_fields() == ['floatcol']

        eq = db.query(ModelForTest).where_tag('t4').eq(50)
        assert eq.find_where_fields() == ['stringcol']

    def test_filter_list(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        eq = db.query(ModelForTest).where('intcol').eq(50)

    def test_eval(self, tmpdir):
        f1 = tmpdir.join("f1.csv")
        # f2 = tmpdir.join("f2.csv")
        f1.write("""intcol,floatcol,stringcol,datecol
100,1.1,foobar0,2020-08-01 17:44:49.732176
50,11.1,foobar1,2020-08-02 17:44:49.732176
100,111.1,foobar2,2020-08-03 17:44:49.732176
50,1111.1,foobar3,2020-08-04 17:44:49.732176
100,11111.1,foobar4,2020-08-05 17:44:49.732176
""")
        db = CsvDatabase(str(tmpdir))
        results = db.query(ModelForTest).where('intcol').eq(50).eval()
        assert len(results) == 2
        assert results[0].intcol == 50
        assert results[1].intcol == 50
        # Why the code below? Because order should not matter.
        intcols = [results[0].floatcol, results[1].floatcol]
        assert 11.1 in intcols
        assert 1111.1 in intcols


class TestWhereOp:
    def test_where_op(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        where = db.query(ModelForTest).where('stringcol')
        assert where.where_fields == ['stringcol']


class TestWhereTagOp:
    def test_where_tag_op(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        where = db.query(ModelForTest).where_tag('t2')
        assert len(where.where_fields) == 2
        assert 'intcol' in where.where_fields
        assert 'floatcol' in where.where_fields


class NonModelForTest(object):
    pass


class TestQueryOp:
    def test_init(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        with pytest.raises(AssertionError) as error:
            db.query(NonModelForTest)
        assert "class 'NonModelForTest' is not a subclass of Model" == str(error.value)

    # def test_eval(self):
    #     assert False

    def test_where(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        with pytest.raises(AssertionError) as error:
            where = db.query(ModelForTest).where('badcol')
        assert "model 'ModelForTest' does not have field 'badcol'" == str(error.value)

    def test_where_tag(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        with pytest.raises(AssertionError) as error:
            where = db.query(ModelForTest).where_tag('badtag')
        assert "model 'ModelForTest' does not have tag 'badtag'" == str(error.value)
