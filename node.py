import math
import random
from copy import deepcopy

import numpy as np

from state import State


class Node:
    def __init__(self, args, state: State, parent=None, last_move=None):
        self.args = args
        self.state = state
        self.parent = parent
        self.last_move = last_move

        self.children = []
        self.expandable_moves = state.legal_moves()

        self.visit_count = 0
        self.value_sum = 0

    def is_fully_expanded(self):
        return len(self.expandable_moves) == 0 and len(self.children) > 0

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
        q_value = ((child.value_sum / child.visit_count) + 1) / 2
        if child.state.jt == 2:
            q_value = 1 - q_value
        return q_value + self.args['C'] * math.sqrt(math.log(self.visit_count) / child.visit_count)

    def expand(self):
        action = random.choice(self.expandable_moves)
        self.expandable_moves.remove(action)

        child_state = deepcopy(self.state)
        child_state.make_move(action)

        child = Node(self.args, child_state, parent=self, last_move=action)
        self.children.append(child)
        return child

    def simulate(self):
        value, is_terminal = self.state.evaluate(self.state.jt), self.state.h0 == 3

        if is_terminal:
            return value

        rollout_state = deepcopy(self.state)
        while True:
            valid_moves = self.state.legal_moves()
            move = random.choice(valid_moves)
            rollout_state.make_move(move)
            value, is_terminal = self.state.evaluate(self.state.jt), self.state.h0 == 3
            if is_terminal:
                return value

    def backpropagate(self, value):
        self.value_sum += value
        self.visit_count += 1

        value = self.state.evaluate(self.state.jt)
        if self.parent is not None:
            self.parent.backpropagate(value)

