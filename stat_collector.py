import random
import json
from time import time
import numpy as np
import torch

from state import State
import minimax
import evaluators
from MCTS import MCTS
from ResNet import ResNet
from AlphaMCTS import AlphaMCTS


class Player:
    def __init__(self, agent):
        self.agent = agent

    def move(self, state):
        print(f'{state.last_move[:1]}/{'w' if state.jt == 1 else 'b'}', end='')


class RandomPlayer(Player):
    def move(self, state):
        move = random.choice(state.legal_moves())
        state.make_move_text(move)
        super().move(state)


class MinimaxPlayer(Player):
    def __init__(self, agent):
        super().__init__(agent)
        if agent['evaluator'] == 'win':
            self.evaluator = evaluators.win
        elif agent['evaluator'] == 'two_in_a_row':
            self.evaluator = evaluators.two_in_a_row

    def move(self, state):
        mm = minimax.minimax(state, 2, 1, evaluator=self.evaluator)
        state.make_move_text(mm[1])
        super().move(state)


class MctsPlayer(Player):
    def __init__(self, agent):
        super().__init__(agent)
        self.mcts = MCTS({'num_searches': agent['num_searches'], 'C': 1.41})

    def move(self, state):
        mcts_probs = self.mcts.search(state)
        move = max(mcts_probs, key=lambda pair: pair[0])[1]
        state.make_move_text(move)
        super().move(state)


class AlphaZeroPlayer(Player):
    def __init__(self, agent):
        super().__init__(agent)
        device = 'cpu'
        training_option = agent['training_data']
        if training_option == "60/3/500":
            training_data_file = 'models/fixed/model_2.pt'
        elif training_option == "120/8/500":
            training_data_file = 'models/search_120_it_8_selfplay_500_epochs4_temp1.25_eps0.25_alpha0.3/model_7.pt'
        elif training_option == "360/8/500":
            training_data_file = 'model_7.pt'
        model = ResNet(State(), 9, 128, device)
        model.load_state_dict(torch.load(training_data_file, map_location=device))
        self.alpha_mcts = AlphaMCTS({'num_searches': 1000, 'C': 1.41, 'dirichlet_epsilon': 0., 'dirichlet_alpha': 0.3}, model)

    def move(self, state):
        mcts_probs = self.alpha_mcts.search(state)
        move = np.argmax(mcts_probs)
        state.make_move(move)
        super().move(state)


def get_player(agent):
    if agent['agent'] == 'random':
        return RandomPlayer(agent)
    elif agent['agent'] == 'minimax':
        return MinimaxPlayer(agent)
    elif agent['agent'] == 'mcts':
        return MctsPlayer(agent)
    elif agent['agent'] == 'alphazero':
        return AlphaZeroPlayer(agent)


def play_games(white_player, black_player, games, random_start):
    white_wins, black_wins, draws = 0, 0, 0
    moves = 0
    white_time, black_time = 0, 0
    for i in range(games):
        random_moves = 3 if random_start else 0
        print(f'\ngame {i+1} {'' if random_start else 'w'}', end='')
        state = State()
        # while not end of the game
        while state.h0 != 3:
            # if board is full
            if state.h.all():
                state.full()
            elif random_moves:
                move = random.choice(state.legal_moves())
                print(f'{'rw' if state.jt == 1 else 'rb'}{move[:1]} {'w' if random_moves == 1 else ''}', end='')
                state.make_move_text(move)
                random_moves -= 1
            else:
                start = time()
                # white moves
                if state.jt == 1:
                    white_player.move(state)
                    white_time += time() - start
                # black moves
                else:
                    black_player.move(state)
                    black_time += time() - start
                moves += 1
        # game ended
        white_win, black_win = state.solved(1), state.solved(2)
        white_wins += white_win and not black_win
        black_wins += black_win and not white_win
        draws += (white_win and black_win) or (not white_win and not black_win)
    result = {
        'white_player': white_player.agent,
        'black_player': black_player.agent,
        'number_of_games': games,
        'average_moves_per_game': moves // games,
        'white_time_per_move': white_time / (moves // 2),
        'black_time_per_move': black_time / (moves // 2),
        'white_wins': white_wins,
        'black_wins': black_wins,
        'draws': draws
    }
    print()
    print(result)
    with open('results_mctsfix.txt', 'a') as result_file:
        json.dump(result, result_file)
        result_file.write('\n')


rc = json.load(open('run_configuration.json'))
for p in rc['players']:
    play_games(get_player(p['white']),
               get_player(p['black']),
               rc['number_of_games'],
               p['random_start'])
