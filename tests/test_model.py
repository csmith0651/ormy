from ormy.model import Model
from ormy.column import *


class ModelForTest(Model):
    __csv_file__ = "f1.csv"
    __table_name__ = "f1"

    columns = [
        Column('intcol', IntegerColumnType(), tags=['t1', 't2']),
        Column('floatcol', FloatColumnType(), tags=['t2', 't3']),
    ]


class TestModel:
    def test_has_field(self):
        assert ModelForTest.has_field('intcol') == True
        assert ModelForTest.has_field('floatcol') == True
        assert ModelForTest.has_field('badcol') == False

    def test_has_tag(self):
        assert ModelForTest.has_tag('t1') == True
        assert ModelForTest.has_tag('t2') == True
        assert ModelForTest.has_tag('t3') == True
        assert ModelForTest.has_tag('t4') == False

