from abc import abstractmethod
from ormy.datatabase_exception import DatabaseException
from ormy.model import Model


class OpError(Exception):
    def __init__(self, message):
        self.message = message


class OpNode(object):
    def __init__(self, parent):
        self.parent = parent

    def exec(self):
        # TODO: should this be abstract too -- if invoked will this call OpNode.eval() ? and will
        #   error out because eval is abstract. I suppose it depends on the type of self -- is
        #   it the child class or cast to OpNode?
        return self.eval()

    @abstractmethod
    def eval(self):
        pass

    def find_in_parents(self, field):
        current = self
        while current is not None:
            if hasattr(current, field):
                return True, getattr(current, field)
            current = current.parent

        return False, None

    def find_columns(self, names):
        found, model = self.find_in_parents('model')
        if not found:
            raise DatabaseException("could not find field '%s' in op chain" % 'model')

        found_columns = []
        for column in model.columns:
            if column.field in names:
                found_columns.append(column)
        return found_columns


class ListResultOpNode(OpNode):
    def __init__(self, parent):
        super().__init__(parent)

    @abstractmethod
    def eval(self):
        pass

    # TODO: how to support multiple comparison operations on the same where clause, e.g.
    #     database.query(Model).where('field1').lte(100).gte(50)
    #   or is that written as:
    #     database.query(Model).where('field1').lte(100).where('field2').gte(50)

    # what operations can happen on a WhereOp?
    # lt, gt, eq, lt
    def eq(self, value):
        return EqOp(value, self)

    def lt(self, value):
        return LtOp(value, self)

    def lte(self, value):
        return LtEOp(value, self)

    def gt(self, value):
        return GtOp(value, self)

    def gte(self, value):
        return GtEOp(value, self)


class RootOp(OpNode):
    def __init__(self):
        super().__init__(None)

    def eval(self):
        return []


def type_str(val):
    return str(type(val).__name__)


class ComparisonOp(ListResultOpNode):
    @abstractmethod
    def perform_comparison(self):
        pass

    def __init__(self, value, parent):
        super().__init__(parent)
        self.comparison_value = value

    def find_where_fields(self):
        current_op = self.parent
        while current_op is not None:
            if isinstance(current_op, WhereOpBase):
                return current_op.where_fields
            current_op = current_op.parent
        raise OpError('no where clause to bind %s to' % type_str(self))

    def filter_list(self, fields, comparison_value, data):
        filtered_list = []
        for item in data:
            for field in fields:
                field_value = getattr(item, field)
                if self.perform_comparison(field_value, comparison_value):
                    filtered_list.append(item)
                    break
        return filtered_list

    def eval(self):
        parent_results = self.parent.eval()
        where_fields = self.find_where_fields()
        where_columns = self.find_columns(where_fields)
        for column in where_columns:
            if not column.compatible_type(self.comparison_value):
                raise OpError('incompatible types value %s (type %s) and column %s (type %s)'
                              % (self.comparison_value, type_str(self.comparison_value), column.field,
                                 type_str(column.column_type)))
        results = self.filter_list(where_fields, self.comparison_value, parent_results)
        return results


class EqOp(ComparisonOp):
    def __init__(self, value, parent):
        super().__init__(value, parent)

    def perform_comparison(self, field_value, comparison_value):
        return field_value == comparison_value


class GtOp(ComparisonOp):
    def __init__(self, value, parent):
        super().__init__(value, parent)

    def perform_comparison(self, field_value, comparison_value):
        return field_value > comparison_value


class GtEOp(ComparisonOp):
    def __init__(self, value, parent):
        super().__init__(value, parent)

    def perform_comparison(self, field_value, comparison_value):
        return field_value >= comparison_value


class LtOp(ComparisonOp):
    def __init__(self, value, parent):
        super().__init__(value, parent)

    def perform_comparison(self, field_value, comparison_value):
        return field_value < comparison_value


class LtEOp(ComparisonOp):
    def __init__(self, value, parent):
        super().__init__(value, parent)

    def perform_comparison(self, field_value, comparison_value):
        return field_value <= comparison_value


class WhereOpBase(ListResultOpNode):
    def __init__(self, parent):
        super().__init__(parent)

    def eval(self):
        return self.parent.eval()


class WhereOp(WhereOpBase):
    def __init__(self, field, parent):
        super().__init__(parent)
        self.where_fields = [field]


class WhereTagOp(WhereOpBase):
    def __init__(self, tag, parent):
        super().__init__(parent)
        self.where_tag = tag

        found, model = self.find_in_parents('model')
        assert found
        tag_columns = list(filter(lambda e: tag in e.tags, model.columns))
        if len(tag_columns) == 0:
            raise OpError("no columns have tag '%s'" % tag)

        self.where_fields = list(map(lambda c: c.field, tag_columns))


class QueryOp(OpNode):
    def __init__(self, source, model, parent):
        super().__init__(parent)
        self.source = source
        assert issubclass(model, Model) == True, "class '%s' is not a subclass of Model" % model.__name__
        self.model = model

    def eval(self):
        parent_results = self.parent.eval()
        model_instances = self.source.load_model(self.model)
        return parent_results + model_instances

    # what operations can happen on a QueryOp result?

    def field(self, field):
        assert self.model.has_field(field), "model '%s' does not have field '%s'" % (self.model.__name__, field)
        return WhereOp(field, self)

    def field_tag(self, tag):
        assert self.model.has_tag(tag), "model '%s' does not have tag '%s'" % (self.model.__name__, tag)
        return WhereTagOp(tag, self)
