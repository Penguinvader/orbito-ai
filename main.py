import random
from copy import deepcopy

import matplotlib.pyplot as plt
import evaluators
from MCTS import MCTS
from ResNet import ResNet
from state import State, InvalidMoveError
import minimax
import numpy as np
import torch

import torch.nn as nn
import torch.nn.functional as F

if __name__ == '__main__':
    a = State()
    # a.h0 = 1
    # a.h = [[0, 1, 2, 1],
    #        [2, 0, 0, 1],
    #        [0, 0, 0, 0],
    #        [0, 2, 0, 2]]
    encoded_state = a.get_encoded_state()
    print(encoded_state)

    tensor_state = torch.tensor(encoded_state).unsqueeze(0)

    model = ResNet(a, 4, 64)

    policy, value = model(tensor_state)
    value = value.item()
    policy = torch.softmax(policy, axis=1).squeeze(0).detach().cpu().numpy()

    print(value, policy)

    mcts_wins, random_wins, draws = 0, 0, 0
    p1_mode = 0
    p2_mode = 0
    mcts = MCTS(args={'num_searches': 1000, 'C': 1.41})
    try:
        for i in range(100):
            a = State()
            while a.h0 != 3:
                a0 = deepcopy(a)
                a.print_grid()
                if 0 not in [n for row in a.h for n in row]:
                    a.full()
                else:
                    player = 'white' if a.jt == 1 else 'black'
                    print(f'Player {player} {'move' if a.h0 == 1 else 'placement'} coordinates (row column):')
                    if player == 'white' and p1_mode == 1:
                        mm = minimax.minimax(a, 2, 1, evaluator=evaluators.two_in_a_row)
                        move = mm[1]
                        print(mm)
                        a.make_move_text(move)
                    elif player == 'white' and p1_mode == 2:
                        mcts_probs = mcts.search(a)
                        print(mcts_probs)
                        move = max(mcts_probs, key=lambda pair: pair[0])[1]
                        print(move)
                        a.make_move_text(move)
                    elif player == 'black' and p2_mode == 1:
                        move = random.choice(a.legal_moves())
                        print(move)
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
            a.print_grid()
            white_win, black_win = a.solved(1), a.solved(2)
            mcts_wins += white_win and not black_win
            random_wins += black_win and not white_win
            draws += white_win and black_win
            print(
                'draw' if white_win and black_win else 'white wins' if white_win else 'black wins' if black_win else 'draw')
    finally:
        print(f'mcts wins:{mcts_wins} random wins:{random_wins} draws:{draws}')

