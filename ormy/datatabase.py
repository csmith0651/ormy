from ormy.query_engine import *
from ormy.datatabase_exception import *


class CodeQueryBase(ABC):
    def __init__(self, context):
        self.context = context
        self.child = None

    @abstractmethod
    def __str__(self):
        pass

    def compile(self):
        return self.context.database.compile(self.context.query)

    def full_str(self):
        if self.context.query is None:
            return ""

        cur = self.context.query
        buf = str(cur)
        cur = cur.child
        while cur is not None:
            buf = buf + "." + str(cur)
            cur = cur.child
        return buf


class QueryNode(CodeQueryBase):
    def __init__(self, model, context):
        super().__init__(context)
        self.model = model

    def field(self, field):
        self.child = FieldNode(field, self.context)
        return self.child

    def exec(self):
        return self.context.eval_query()

    def __str__(self):
        return "query(model='%s')" % self.model.__name__


class FieldNode(CodeQueryBase):
    def __init__(self, field, context):
        # TODO: check to see if the field is legal for this model to create a compile time-error rather than
        #   a query-time execution error.
        super().__init__(context)
        self.field = field

    def eq(self):
        self.child = EqNode(self.context)
        return self.child

    def __str__(self):
        return "field('%s')" % self.field

# TODO: Add support for AndNode and OrNode to support complex boolean queries.


class CompNode(CodeQueryBase):
    def __init__(self, context):
        super().__init__(context)

    def value(self, value):
        self.child = Value(value, self.context)
        return self.child

    def field(self, field):
        self.child = FieldNode(field, self.context)
        return self.child

    @abstractmethod
    def __str__(self):
        pass


class EqNode(CompNode):
    def __init__(self, context):
        super().__init__(context)

    def __str__(self):
        return "eq()"


class Value(CodeQueryBase):
    def __init__(self, value, context):
        super().__init__(context)
        self.value = value

    def exec(self):
        return self.context.eval_query()

    def __str__(self):
        return "value(%s)" % self.value


class Database(ABC):
    def __init__(self, engine=None):
        self.query_engine = QueryEngine() if engine is None else engine

    def query(self, model):
        context = QueryContext(self, None)
        query = QueryNode(model, context)
        context.query = query
        return query

    @classmethod
    def _convert_query_to_raw_expressions(cls, query):
        ret = []
        while query is not None:
            if isinstance(query, Value):
                ret.append(ValueExpr(query.value))
            elif isinstance(query, EqNode):
                ret.append(EqExpr())
            elif isinstance(query, FieldNode):
                ret.append(FieldExpr(query.field))
            elif isinstance(query, QueryNode):
                ret.append(QueryExpr(query.model))
            else:
                raise DatabaseException('unknown query object "%s"' % query.__name__)

            query = query.child

        return ret

    def eval(self, query):
        expr_list = Database._convert_query_to_raw_expressions(query)
        return self.query_engine.eval(expr_list)

    def compile(self, query):
        """return the expression tree"""
        expr_list = Database._convert_query_to_raw_expressions(query)
        return self.query_engine.compile(expr_list)
