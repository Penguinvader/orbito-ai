import numpy as np
import torch

from AlphaMCTS import AlphaMCTS
from state import State

from tqdm.notebook import trange


class AlphaZero:
    def __init__(self, model, optimizer, state, args):
        self.model = model
        self.optimizer = optimizer
        self.state = state
        self.args = args
        self.mcts = AlphaMCTS(args, model)

    def self_play(self):
        memory = []
        jt = 1
        state = State()

        while True:
            action_probs = self.mcts.search(state)

            memory.append((state, action_probs, jt))

            action = np.random.choice(len(state.moves), p=action_probs)

            state.make_move(action)

            value, is_terminal = state.evaluate(jt), state.h0 == 3

            if is_terminal:
                return_memory = []
                for hist_state, hist_action_probs, hist_jt in memory:
                    hist_outcome = value if hist_jt == jt else -value
                    return_memory.append((
                        hist_state.get_encoded_state(),
                        hist_action_probs,
                        hist_outcome
                    ))
                return return_memory

            jt = state.jt




    def train(self, memory):
        pass

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



