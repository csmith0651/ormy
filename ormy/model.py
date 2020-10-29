# TODO:
#   - Separate CsvData models from other models
#   - Insure that the proper values are set on CsvData Model objects (e.g. __csv_file__, et cetera)
#   - Ensure that columns field is populated

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
