from abc import abstractmethod, ABC


class QueryEngineException(Exception):
    def __init__(self, message):
        self.message = message


class Expr(ABC):
    def __init__(self):
        self.left = None
        self.right = None

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self))

    def children(self, left, right=None):
        self.left = left
        if right:
            self.right = right
        return self

    @abstractmethod
    def is_operand(self) -> bool:
        pass

    @abstractmethod
    def is_operator(self) -> bool:
        pass

    @classmethod
    def attach_operands(cls, expr, children):
        assert len(children) in [1, 2]
        expr.left = children[0]
        if len(children) == 2:
            expr.right = children[1]
        return expr


class OperatorExpr(Expr):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def operand_count(self):
        pass

    def is_operator(self):
        return True

    def is_operand(self):
        return False

    @abstractmethod
    def precedence(self):
        pass

    def __eq__(self, other):
        return super().__eq__(other)

    def __str__(self):
        parent = super().__str__()
        return parent + "precedent=%d"


class OperandExpr(Expr):
    def __init__(self):
        super().__init__()

    def is_operator(self):
        return False

    def is_operand(self):
        return True

    def __eq__(self, other):
        return super().__eq__(other)


class ValueExpr(OperandExpr):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return "value(%s)" % self.value

    def __eq__(self, other):
        return super().__eq__(other) and (self.value == other.value)


class CompExpr(OperatorExpr):
    def __init__(self, op_str):
        super().__init__()
        self.op_str = op_str

    def operand_count(self):
        return 2

    def precedence(self):
        # TODO: fill in with proper precedence
        return 12

    @abstractmethod
    def perform_compare(self, a, b):
        pass

    def __str__(self):
        return "%s( %s ,%s )" % (self.op_str, self.left, self.right)

    def __eq__(self, other):
        return super().__eq__(other) and self.left == other.left and self.right == other.right


class ConjunctionExpr(OperatorExpr):
    def __init__(self):
        super().__init__()

    def operand_count(self):
        return 2

    @abstractmethod
    def precedence(self):
        pass


class OrExpr(ConjunctionExpr):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return 'or( %s , %s )' % (self.left, self.right)

    def precedence(self):
        return 9


class AndExpr(ConjunctionExpr):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return 'and( %s , %s )' % (self.left, self.right)

    def precedence(self):
        return 10


class EqExpr(CompExpr):
    def __init__(self):
        super().__init__('eq')

    def perform_compare(self, a, b):
        return a == b


class FieldExpr(OperandExpr):
    def __init__(self, field):
        self.field = field
        super().__init__()

    def __str__(self):
        return "field('%s')" % self.field

    def __eq__(self, other):
        return super().__eq__(other) and self.field == other.field


class LambdaExpr(OperandExpr):
    """Not intended to use in the query, but useful for internal operations. Inject an arbitrary
       lambda function into the AST for delay evaluation."""
    def __init__(self, func, expr):
        super().__init__()
        self.func = func
        self.left = expr

    def __str__(self):
        return "lambda()"

    def __eq__(self, other):
        return super().__eq__(other) and self.func == other.func


class QueryExpr(OperatorExpr):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.left = None

    def precedence(self):
        return 2

    def operand_count(self):
        return 1

    def __eq__(self, other):
        return super().__eq__(other) and (self.model == other.model) and (self.left == other.left)

    def __str__(self):
        return "query( %s )" % self.model.__name__


class QueryContext(object):
    def __init__(self, database, query):
        self.database = database
        self.query = query

    def __str__(self):
        return "QueryContext(%s, %s)" % (self.database, self.query.full_str())

    def eval_query(self):
        return self.database.eval(self.query)


class ExprContext(object):
    def __init__(self):
        self.model_data = None


class QueryEngine(ABC):
    def __init__(self):
        pass

    _TRUE = ValueExpr(True)
    _FALSE = ValueExpr(False)

    def compile(self, expr_list):
        # TODO: do I want to wrap the compiled expression tree in a CompiledQuery class?
        return self.convert_expr_list_to_expr_tree(expr_list)

    def _run(self, expr, context: ExprContext):
        # Note: don't make this abstract so we can test the platform independent functionality of the QueryEngine.
        pass

    def eval(self, expr_list):
        expr = self.compile(expr_list)
        return self._run(expr, ExprContext())

    @classmethod
    def optimize_simple_expr(cls, expr_list):
        # some cases are common and can be optimized quickly
        if len(expr_list) == 1 and isinstance(expr_list[0], QueryExpr):
            # this is a simple query(Model).exec()
            return QueryEngine.generate_query_all_expr(expr_list[0])
        return None

    # noinspection SpellCheckingInspection
    @classmethod
    def convert_expr_list_to_expr_tree(cls, expr_list):
        if not expr_list:
            return None

        expr = QueryEngine.optimize_simple_expr(expr_list)
        if expr is not None:
            return expr

        # cases of operator consumption
        # - if operator stack is empty, operand stack is 1, and input is empty then top of stack is AST and return.
        # - current is operator and is higher precedence than what is on operator stack (if operator stack is empty,
        #   current operator is higher precedence)
        #   - not enough operands, push operator on operator stack, continue reading from input
        #   - enough operands, use current operator, consume required operands, and push new operand (combined tree) to
        #     operand stack.
        # - current is operator and is lower precedence than what is on the operator stack (if current operator is empty
        #   it is lower precedence)
        #   - not enough operands, error
        #   - enough operands, pop operator off stack, consume required operands, push new operand (combined tree) to
        #     operand stack
        #   - do not consume current operator from input (need to compare it to the new head of the operator stack)
        # - current is operand, push on to operand stack

        # # db.query(Model).field('f1').eq().value(5).exec()

        ator_stack = []
        and_stack = []
        expr_pos = 0
        cur_expr = expr_list[expr_pos]

        while True:
            if len(ator_stack) == 0 and cur_expr is None:
                break

            if cur_expr is None:
                top = ator_stack.pop()
                if len(and_stack) < top.operand_count():
                    raise QueryEngineException('for operator "%s" insufficient operands (need %d only %d on stack)'
                                               % (top.__name__, top.operand_count(), len(and_stack)))
                last_n = -1*top.operand_count()
                Expr.attach_operands(top, and_stack[last_n:])
                del and_stack[last_n:]
                and_stack.append(top)
            elif cur_expr.is_operand():
                and_stack.append(cur_expr)
                cur_expr = None
            elif cur_expr.is_operator() and (not ator_stack or cur_expr.precedence() >= ator_stack[-1].precedence()):
                # top of operator stack is lower precedence than cur_expr so push on the stack.
                ator_stack.append(cur_expr)
                cur_expr = None
            elif cur_expr.is_operator():
                # top of operator stack is higher precedence, construct a tree from that operator and push back on stack
                top = ator_stack.pop()
                if len(and_stack) < top.operand_count():
                    raise QueryEngineException('for operator "%s" insufficient operands (need %d only %d on stack)'
                                               % (top.__name__, top.operand_count(), len(and_stack)))
                last_n = -1*top.operand_count()
                Expr.attach_operands(top, and_stack[last_n:])
                del and_stack[last_n:]
                and_stack.append(top)
            else:
                raise QueryEngineException("expr to AST unknown state")

            if cur_expr is None and (expr_pos + 1) < len(expr_list):
                expr_pos = expr_pos + 1
                cur_expr = expr_list[expr_pos]

        if len(and_stack) != 1:
            raise QueryEngineException('Expr construction error, input and operator stack exhausted but operand stack"'
                                       + ' is len %d' % len(and_stack))

        return and_stack.pop()

    @classmethod
    def generate_query_all_expr(cls, expr) -> Expr:
        Expr.attach_operands(expr, [QueryEngine._TRUE])
        return expr
