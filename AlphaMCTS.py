import numpy as np

import evaluators
from AlphaNode import Node
import torch


class AlphaMCTS:
    def __init__(self, args, model):
        self.args = args
        self.model = model

    @torch.no_grad()
    def search(self, state):
        root = Node(self.args, state)

        for search in range(self.args['num_searches']):
            node = root

            while node.is_fully_expanded():
                node = node.select()

            value, is_terminal = node.state.evaluate(node.state.jt), node.state.h0 == 3

            if not is_terminal:
                policy, value = self.model(
                    torch.tensor(node.state.get_encoded_state(), device=self.model.device).unsqueeze(0)
                )
                policy = torch.softmax(policy, axis=1).squeeze(0).cpu().numpy()
                valid_moves = node.state.legal_moves_numeric()
                policy = policy * valid_moves
                policy /= np.sum(policy)

                value = value.item()

                node.expand(policy)

            node.backpropagate(value)

        action_probs = np.zeros(len(state.moves))
        for child in root.children:
            action_probs[child.last_move] = child.visit_count
        action_probs /= np.sum(action_probs)
        return action_probs

