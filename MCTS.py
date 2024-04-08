import numpy as np

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

            value, is_terminal = node.state.evaluate(node.state.jt), node.state.h0 == 3

            if not is_terminal:
                node = node.expand()
                value = node.simulate()

            node.backpropagate(value)

        action_probs = np.array([child.visit_count for child in root.children], np.float64)
        action_probs /= np.sum(action_probs)
        return tuple(zip(action_probs, [child.last_move for child in root.children]))

