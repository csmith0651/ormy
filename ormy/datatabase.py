from abc import abstractmethod

# from ormy.model import Model
from ormy.ops import RootOp, QueryOp

class Database(object):
    def __init__(self):
        pass

    def query(self, model):
        # assert issubclass(model, Model)
        # TODO: I don't think RootOp is necessary
        root_op = RootOp()
        return QueryOp(self, model, root_op)

    @abstractmethod
    def load_model(self, model):
        pass
