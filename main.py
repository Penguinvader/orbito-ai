import random
from copy import deepcopy

import matplotlib.pyplot as plt
import evaluators
from AlphaMCTS import AlphaMCTS
from AlphaZero import AlphaZero
from MCTS import MCTS
from ResNet import ResNet
from state import State, InvalidMoveError
import minimax
import numpy as np
import torch

import torch.nn as nn

from tqdm.notebook import trange

if __name__ == '__main__':
    a = State()
    # a.h0 = 1
    # a.h = np.array([[0, 2, 2, 1],
    #                 [2, 0, 0, 2],
    #                 [0, 0, 0, 0],
    #                 [0, 2, 0, 2]])
    # encoded_state = a.get_encoded_state()
    # print(encoded_state)
    #
    # tensor_state = torch.tensor(encoded_state).unsqueeze(0)
    #
    # model = ResNet(a, 4, 64)
    #
    # policy, value = model(tensor_state)
    # value = value.item()
    # policy = torch.softmax(policy, axis=1).squeeze(0).detach().cpu().numpy()
    #
    # print(value, policy)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    white_wins, black_wins, draws = 0, 0, 0
    # 1: random, 2: mcts, 3: alpha_mcts1 4: alpha_mcts2 5: minimax
    p1_mode = 2
    p2_mode = 3
    basic_mcts = MCTS({'num_searches': 1000, 'C': 1.41})
    model = ResNet(a, 4, 64)
    # model.load_state_dict(torch.load('model_2.pt', map_location=device))
    mcts = AlphaMCTS({'num_searches': 1000, 'C': 1.41}, model)
    model2 = ResNet(a, 4, 64)
    # model2.load_state_dict(torch.load('models/model_2.pt', map_location=device))
    mcts2 = AlphaMCTS({'num_searches': 1000, 'C': 1.41}, model2)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    # optimizer.load_state_dict(torch.load('optimizer_2.pt', map_location=device))
    optimizer2 = torch.optim.Adam(model.parameters(), lr=0.001)
    # optimizer2.load_state_dict(torch.load('models/optimizer_2.pt', map_location=device))

    args = {
        'C': 2,
        'num_searches': 60,
        'num_iterations': 3,
        'num_self_play_iterations': 500,
        'num_epochs': 4,
        'batch_size': 64
    }

    alpha_zero = AlphaZero(model, optimizer, a, args)

    # alpha_zero.learn()

    model.eval()
    model2.eval()

    try:
        for i in range(100):
            random_moves = 0
            a = State()
            a.h0 = 1
            a.jt = 2
            a.h = np.array([[0, 2, 1, 2],
                            [1, 0, 0, 2],
                            [0, 0, 0, 0],
                            [0, 0, 1, 1]])
            # a.h = np.array([[0, 1, 2, 1],
            #                 [2, 0, 0, 1],
            #                 [0, 0, 0, 0],
            #                 [0, 0, 2, 2]])
            while a.h0 != 3:
                a0 = deepcopy(a)
                a.print_grid()
                if 0 not in [n for row in a.h for n in row]:
                    a.full()
                else:
                    player = 'white' if a.jt == 1 else 'black'
                    print(f'Player {player} {'move' if a.h0 == 1 else 'placement'} coordinates (row column):')
                    if random_moves > 0 or player == 'white' and p1_mode == 1 or player == 'black' and p2_mode == 1:
                        move = random.choice(a.legal_moves())
                        print('random ' + move)
                        a.make_move_text(move)
                    elif player == 'white' and p1_mode == 2 or player == 'black' and p2_mode == 2:
                        mcts_probs = basic_mcts.search(a)
                        print(mcts_probs)
                        move = max(mcts_probs, key=lambda pair: pair[0])[1]
                        print(move)
                        a.make_move_text(move)
                    elif player == 'white' and p1_mode == 3 or player == 'black' and p2_mode == 3:
                        mcts_probs = mcts.search(a)
                        print([(a.moves[i], prob) for i, prob in enumerate(mcts_probs) if prob])
                        move = np.argmax(mcts_probs)
                        print(a.moves[move])
                        a.make_move(move)
                    elif player == 'white' and p1_mode == 4 or player == 'black' and p2_mode == 4:
                        mcts_probs = mcts2.search(a)
                        print([(a.moves[i], prob) for i, prob in enumerate(mcts_probs) if prob])
                        move = np.argmax(mcts_probs)
                        print(a.moves[move])
                        a.make_move(move)
                    elif player == 'white' and p1_mode == 5 or player == 'black' and p2_mode == 5:
                        mm = minimax.minimax(a, 2, 1, evaluator=evaluators.two_in_a_row)
                        move = mm[1]
                        print(mm)
                        a.make_move_text(move)
                    else:
                        try:
                            i, j = (int(n) for n in input().split())
                            if a.h0 == 1:
                                print(f'Player {player} move direction (up down left right skip)')
                                match input().lower():
                                    case "up":
                                        a.up(i, j)
                                    case "down":
                                        a.down(i, j)
                                    case "left":
                                        a.left(i, j)
                                    case "right":
                                        a.right(i, j)
                                    case _:
                                        print('Movement skipped.')
                                        a.skip_move()
                            elif a.h0 == 2:
                                a.place(i, j)
                        except (ValueError, IndexError, InvalidMoveError):
                            print('Invalid input.')
                            a = a0
                            if a.h0 == 1:
                                print('Movement skipped.')
                                a.skip_move()
                if random_moves > 0:
                    random_moves -= 1
            a.print_grid()
            white_win, black_win = a.solved(1), a.solved(2)
            white_wins += white_win and not black_win
            black_wins += black_win and not white_win
            draws += white_win and black_win
            print(
                'draw' if white_win and black_win else 'white wins' if white_win else 'black wins' if black_win else 'draw')
    finally:
        print(f'white wins:{white_wins} black wins:{black_wins} draws:{draws}')
