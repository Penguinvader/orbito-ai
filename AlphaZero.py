import random

import numpy as np
import torch
import torch.nn.functional as F

from AlphaMCTS import AlphaMCTS
from state import State

from tqdm import trange


class AlphaZero:
    def __init__(self, model, optimizer, state, args):
        self.model = model
        self.optimizer = optimizer
        self.state = state
        self.args = args
        self.mcts = AlphaMCTS(args, model)

    def self_play(self):
        memory = []
        state = State()

        while True:
            action_probs = self.mcts.search(state)

            memory.append((state, action_probs, state.jt))

            action = np.random.choice(len(state.moves), p=action_probs)

            state.make_move(action)

            value, is_terminal = state.evaluate(state.jt), state.h0 == 3

            if is_terminal:
                return_memory = []
                for hist_state, hist_action_probs, hist_jt in memory:
                    hist_outcome = value if hist_jt == state.jt else -value
                    return_memory.append((
                        hist_state.get_encoded_state(),
                        hist_action_probs,
                        hist_outcome
                    ))
                return return_memory





    def train(self, memory):
        random.shuffle(memory)
        for batch_idx in range(0, len(memory), self.args['batch_size']):
            sample = memory[batch_idx:min(len(memory)-1, batch_idx + self.args['batch_size'])]
            state, policy_targets, value_targets = zip(*sample)

            state, policy_targets = np.array(state), np.array(policy_targets)

            value_targets = np.array(value_targets).reshape(-1, 1)
            state = torch.tensor(state, dtype=torch.float32)
            policy_targets = torch.tensor(policy_targets, dtype=torch.float32)
            value_targets = torch.tensor(value_targets, dtype=torch.float32)

            out_policy, out_value = self.model(state)

            policy_loss = F.cross_entropy(out_policy, policy_targets)
            value_loss = F.mse_loss(out_value, value_targets)
            loss = policy_loss + value_loss

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()


    def learn(self):
        for iteration in trange(self.args['num_iterations']):
            memory = []

            self.model.eval()
            for self_play_iteration in trange(self.args['num_self_play_iterations']):
                memory += self.self_play()

            self.model.train()
            for epoch in range(self.args['num_epochs']):
                self.train(memory)

            torch.save(self.model.state_dict(), f'model_{iteration}.pt')
            torch.save(self.optimizer.state_dict(), f'optimizer_{iteration}.pt')



