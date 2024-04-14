import math
import random
from copy import deepcopy

import numpy as np

from state import State


class Node:
    def __init__(self, args, state: State, parent=None, last_move=None, prior=0, visit_count=0):
        self.args = args
        self.state = state
        self.parent = parent
        self.last_move = last_move
        self.prior = prior

        self.children = []

        self.visit_count = visit_count
        self.value_sum = 0

    def is_fully_expanded(self):
        return len(self.children) > 0

    def select(self):
        best_child = None
        best_ucb = -np.inf

        for child in self.children:
            ucb = self.get_ucb(child)
            if ucb > best_ucb:
                best_child = child
                best_ucb = ucb

        return best_child

    def get_ucb(self, child):
        if child.visit_count == 0:
            q_value = 0.0
        else:
            q_value = ((child.value_sum / child.visit_count) + 1) / 2
        if child.state.jt == 3 - self.state.jt:
            q_value = 1.0 - q_value
        return q_value + self.args['C'] * (math.sqrt(self.visit_count) / (child.visit_count + 1)) * child.prior

    def expand(self, policy):
        for action, prob in enumerate(policy):
            if prob > 0:
                child_state = deepcopy(self.state)
                child_state.make_move(action)

                child = Node(self.args, child_state, parent=self, last_move=action, prior=prob)
                self.children.append(child)
        return child

    def backpropagate(self, value):
        self.value_sum += value
        self.visit_count += 1

        if self.parent is not None:
            value = value if self.parent.state.jt == self.state.jt else -value
            self.parent.backpropagate(value)

