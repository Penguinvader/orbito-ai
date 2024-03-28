from copy import deepcopy
from random import shuffle
from state import State, InvalidMoveError
from minimax import minimax


if __name__ == '__main__':
    a = State()
    a.h0 = 1
    a.h = [[0, 2, 0, 0],
           [2, 0, 0, 1],
           [0, 0, 0, 2],
           [0, 0, 1, 1]]

    ai_mode = 1
    while a.h0 != 3:
        a0 = deepcopy(a)
        a.print_grid()
        if 0 not in [n for row in a.h for n in row]:
            a.full()
        else:
            player = 'white' if a.jt == 1 else 'black'
            print(f'Player {player} {'move' if a.h0 == 1 else 'placement'} coordinates (row column):')
            if player == 'white' and ai_mode == 1:
                mm = minimax(a, 2, 1)
                move = mm[1]
                print(mm)
                if move == 'skip':
                    a.skip_move()
                else:
                    a.make_move(*move.split())
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
    print('draw' if white_win and black_win else 'white wins' if white_win else 'black wins' if black_win else '?????')
