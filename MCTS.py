import evaluators
from node import Node


class MCTS:
    def __init__(self, args):
        self.args = args

    def search(self, state):
        root = Node(self.args, state)

        for search in range(self.args['num_searches']):
            node = root

            while node.is_fully_expanded():
                node = node.select()

            value, is_terminal = node.state.evaluate(1), node.state.h0 == 3

            if not is_terminal:
                node = node.expand()
                # expansion
                # simulation
            # backpropagation

        # return visit_counts
