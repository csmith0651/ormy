import pytest

from ormy.column import *
from ormy.model import Model, ModelException
from tests.models_for_testing import AllValueTypes, \
    IntSingle, FloatSingle, StringSingle, DateSingle, TIME_STR, ModelLevel3, ModelLevel2, ModelLevel1


class ModelForTest(Model):
    __csv_file__ = "f1.csv"

    columns = [
        Column('int_col', IntegerColumnType(), tags=['t1', 't2']),
        Column('float_col', FloatColumnType(), tags=['t2', 't3']),
    ]


class TestModel:
    def test_has_field(self):
        assert ModelForTest.has_field('int_col')
        assert ModelForTest.has_field('float_col')
        assert not ModelForTest.has_field('bad_col')

    def test_has_tag(self):
        assert ModelForTest.has_tag('t1')
        assert ModelForTest.has_tag('t2')
        assert ModelForTest.has_tag('t3')
        assert not ModelForTest.has_tag('t4')

    def test_create_single_type_in_object(self):
        m_int = IntSingle.create({'value': 100})
        assert m_int.value == 100
        assert len(m_int.__dict__) == 1
        m_float = FloatSingle.create({'value': 3.14})
        assert m_float.value == 3.14
        assert len(m_float.__dict__) == 1
        m_string = StringSingle.create({'value': 'foobar'})
        assert m_string.value == 'foobar'
        assert len(m_string.__dict__) == 1
        m_date = DateSingle.create({'value': datetime.strptime(TIME_STR, AllValueTypes.ALL_VALUE_TYPES_FORMAT_STR)})
        assert m_date.value == datetime.strptime(TIME_STR, AllValueTypes.ALL_VALUE_TYPES_FORMAT_STR)
        assert len(m_date.__dict__) == 1

    def test_create_flat_all_values(self):
        m = AllValueTypes.create({'int_col': 100, 'float_col': 99.99, 'string_col': 'foobar',
                                  'date_col': datetime.strptime(TIME_STR,
                                                                AllValueTypes.ALL_VALUE_TYPES_FORMAT_STR)})
        assert m.int_col == 100
        assert m.float_col == 99.99
        assert m.string_col == 'foobar'
        assert m.date_col == datetime.strptime(TIME_STR,
                                               AllValueTypes.ALL_VALUE_TYPES_FORMAT_STR)
        assert len(m.__dict__) == 4

    def test_create_complex(self):
        l1 = ModelLevel1()
        l2 = ModelLevel2()
        l3 = ModelLevel3()
        l1.id = 1
        l1.value = 1
        l1.level2_id = 2
        l1.level2 = l2
        l2.id = 2
        l2.value = 50
        l2.level3_id = 3
        l2.level3 = l3
        l3.id = 3
        l3.value = 100

        l1 = ModelLevel1.create({
            'id': 1,
            'value': 1,
            'level2_id': 2,
            'level2': ModelLevel2.create({
                'id': 2,
                'value': 50,
                'level3_id': 3,
                'level3': ModelLevel3.create({
                    'id': 3,
                    'value': 100
                })
            })
        })

        assert l1.id == 1
        assert l1.value == 1
        assert l1.level2_id == 2
        assert isinstance(l1.level2, ModelLevel2)
        assert len(l1.__dict__) == 4
        l2 = l1.level2
        assert l2.id == 2
        assert l2.value == 50
        assert l2.level3_id == 3
        assert isinstance(l2.level3, ModelLevel3)
        assert len(l2.__dict__) == 4
        l3 = l2.level3
        assert l3.id == 3
        assert l3.value == 100
        assert len(l3.__dict__) == 2

    def test_create_no_obj_for_fk(self):
        with pytest.raises(ModelException) as err:
            ModelLevel2.create({
                'id': 2,
                'value': 50,
                'level3_id': 3,
            })
        err_str = 'for foreign key "level3_id" must define object field with key "level3" value'
        assert err_str == str(err.value)

    def test_compare(self):
        test_data = [
            (IntSingle, {'value': 99}, 'foobar'),
            (FloatSingle, {'value': 3.14}, datetime.strptime(TIME_STR, AllValueTypes.ALL_VALUE_TYPES_FORMAT_STR)),
            (StringSingle, {'value': 'foobar'}, 100),
            (DateSingle, {'value': datetime.strptime(TIME_STR, AllValueTypes.ALL_VALUE_TYPES_FORMAT_STR)}, 3.14)
        ]
        for test in test_data:
            model = test[0]
            values = test[1]
            bad_value = test[2]
            ent1 = model.create(values)
            ent2 = model.create(values)
            assert Model.compare(ent1, ent2)
            ent1.value = bad_value
            assert not Model.compare(ent1, ent2)

    def test_compare_diff_model(self):
        class M1(Model):
            columns = [Column('value', IntegerColumnType())]

        class M2(Model):
            columns = [Column('value', IntegerColumnType())]

        m1 = M1.create({'value': 100})
        m2 = M2.create({'value': 100})

        assert not Model.compare(m1, m2)

    def test_compare_complex(self):
        l1 = ModelLevel1.create({
            'id': 1,
            'value': 1,
            'level2_id': 2,
            'level2': ModelLevel2.create({
                'id': 2,
                'value': 50,
                'level3_id': 3,
                'level3': ModelLevel3.create({
                    'id': 3,
                    'value': 100
                })
            })
        })

        l2 = ModelLevel1.create({
            'id': 1,
            'value': 1,
            'level2_id': 2,
            'level2': ModelLevel2.create({
                'id': 2,
                'value': 50,
                'level3_id': 3,
                'level3': ModelLevel3.create({
                    'id': 3,
                    'value': 100
                })
            })
        })

        assert Model.compare(l1, l2)

        l2.level2_id = 4
        l2.level2.id = 4
        l2.level2.level3_id = 5
        l2.level2.level3.id = 5
        assert not Model.compare(l1, l2)
