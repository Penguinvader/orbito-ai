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
        root = Node(self.args, state, visit_count=1)
        policy, _ = self.model(
            torch.tensor(state.get_encoded_state(), device=self.model.device).unsqueeze(0)
        )
        policy = torch.softmax(policy, dim=1).squeeze(0).cpu().numpy()
        policy = ((1 - self.args['dirichlet_epsilon']) * policy + self.args['dirichlet_epsilon'] *
                  np.random.dirichlet([self.args['dirichlet_alpha']] * len(state.moves)))
        valid_moves = state.legal_moves_numeric()
        policy *= valid_moves
        policy /= np.sum(policy)
        root.expand(policy)

        for search in range(self.args['num_searches']):
            node = root

            while node.is_fully_expanded():
                # pick greatest UCB child
                node = node.select()

            # check if the game is over and evaluate it for the final player
            value, is_terminal = node.state.evaluate(node.state.jt), node.state.h0 == 3

            if not is_terminal:
                # if it's not over, get the policy and value for this child from the model
                policy, value = self.model(
                    torch.tensor(node.state.get_encoded_state(), device=self.model.device).unsqueeze(0)
                )
                policy = torch.softmax(policy, dim=1).squeeze(0).cpu().numpy()
                valid_moves = node.state.legal_moves_numeric()
                policy = policy * valid_moves
                policy /= np.sum(policy)

                value = value.item()
                # if it's not over, fill out all the children of this child node
                node.expand(policy)

            # backpropagate from this current child node with whatever value the neural network spat out
            node.backpropagate(value)

        action_probs = np.zeros(len(state.moves))
        for child in root.children:
            action_probs[child.last_move] = child.visit_count
        action_probs /= np.sum(action_probs)
        return action_probs
