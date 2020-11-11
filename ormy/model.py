# TODO:
#   - Separate CsvData models from other models
#   - Insure that the proper values are set on CsvData Model objects (e.g. __csv_file__, et cetera)
#   - Ensure that columns field is populated

class ModelException(Exception):
    def __init__(self, message):
        self.message = message


class Model(object):
    columns = None

    def __init__(self):
        pass

    @classmethod
    def has_field(cls, field):
        for column in cls.columns:
            if column.field == field:
                return True
        return False

    @classmethod
    def has_tag(cls, tag):
        for c in cls.columns:
            if tag in c.tags:
                return True
        return False

    @classmethod
    def get_field_names(cls):
        return [c for c in cls.columns]

    @classmethod
    def __str__(cls):
        return "Model(name='%s', fields='%s')" % (cls.__name___, cls.get_field_names())

    @classmethod
    def get_fk_columns(cls):
        return [c for c in cls.columns if c.has_fk()]

    @classmethod
    def create(cls, values):
        obj = cls()
        for c in cls.columns:
            c.set_field(obj, values.get(c.field))
            if c.has_fk():
                of = c.object_field
                if of not in values:
                    raise ModelException('for foreign key "%s" must define object field with key "%s" value'
                                         % (c.field, of))
                setattr(obj, of, values.get(of))
        return obj

    @staticmethod
    def get_pk_value(entity):
        assert isinstance(entity, Model)

        pk_column = entity.get_pk_column()
        assert pk_column is not None
        pk_field = entity.get_pk_field()

        return getattr(entity, pk_field)

    def get_pk_column(self):
        for c in self.columns():
            if c.is_primary_key():
                return c
        return None

    def get_pk_field(self):
        col = self.get_pk_column()
        return None if col is None else col.field

    @classmethod
    def compare(cls, ent1, ent2):
        if not isinstance(ent1, Model):
            return False
        if type(ent1) != type(ent2):
            return False
        for c in type(ent1).columns:
            if c.has_field(ent1) != c.has_field(ent2):
                return False
            if c.get_field(ent1) != c.get_field(ent2):
                return False
            if c.has_fk():
                fk_ent1 = getattr(ent1, c.object_field)
                fk_ent2 = getattr(ent2, c.object_field)
                if not cls.compare(fk_ent1, fk_ent2):
                    return False

        return True
