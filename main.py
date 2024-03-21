from copy import deepcopy
from random import choice, shuffle


class InvalidMoveError(Exception):
    pass


class State:
    rotation_matrix = [[(0, 1), (0, 2), (0, 3), (1, 3)],
                       [(0, 0), (1, 2), (2, 2), (2, 3)],
                       [(1, 0), (1, 1), (2, 1), (3, 3)],
                       [(2, 0), (3, 0), (3, 1), (3, 2)]]

    def __init__(self):
        self.h0 = 2
        self.jt = 1
        self.h = [[0 for col in range(4)] for row in range(4)]

    def print_grid(self):
        for row in self.h:
            print("".join("⚪" if j == 1 else "⚫" if j == 2 else "⭕" for j in row))

    def constraint(self):
        whites = sum(row.count(1) for row in self.h)
        blacks = sum(row.count(2) for row in self.h)
        return (self.jt == 1 and whites == blacks) or (self.jt == 2 and whites == blacks + 1)

    def solved(self, jt):
        sets = []
        for row in self.h:
            sets.append(set(row))
        for col in zip(*self.h):
            sets.append(set(col))
        sets.append({self.h[0][0], self.h[1][1], self.h[2][2], self.h[3][3]})
        sets.append({self.h[3][0], self.h[2][1], self.h[1][2], self.h[0][3]})
        for s in sets:
            if s == {jt}:
                return True
        return False

    def rotate(self):
        rotated = [[self.h[col[0]][col[1]] for col in row] for row in self.rotation_matrix]
        self.h = rotated

    def up(self, i, j):
        if self.h[i][j] == 3 - self.jt and self.h[i - 1][j] == 0 and self.h0 == 1:
            self.h[i - 1][j] = self.h[i][j]
            self.h[i][j] = 0
            self.h0 = 2
        else:
            raise InvalidMoveError

    def down(self, i, j):
        if self.h[i][j] == 3 - self.jt and self.h[i + 1][j] == 0 and self.h0 == 1:
            self.h[i + 1][j] = self.h[i][j]
            self.h[i][j] = 0
            self.h0 = 2
        else:
            raise InvalidMoveError

    def left(self, i, j):
        if self.h[i][j] == 3 - self.jt and self.h[i][j - 1] == 0 and self.h0 == 1:
            self.h[i][j - 1] = self.h[i][j]
            self.h[i][j] = 0
            self.h0 = 2
        else:
            raise InvalidMoveError

    def right(self, i, j):
        if self.h[i][j] == 3 - self.jt and self.h[i][j + 1] == 0 and self.h0 == 1:
            self.h[i][j + 1] = self.h[i][j]
            self.h[i][j] = 0
            self.h0 = 2
        else:
            raise InvalidMoveError

    def skip_move(self):
        if self.h0 == 1:
            self.h0 = 2
        else:
            raise InvalidMoveError

    def place(self, i, j):
        if self.h[i][j] == 0 and self.h0 == 2:
            self.h[i][j] = self.jt
            self.rotate()
            self.h0 = 3 if self.solved(1) or self.solved(2) else 1
            self.jt = 3 - self.jt
        else:
            raise InvalidMoveError

    def full(self):
        self.h0 = 3
        for n in range(5):
            self.rotate(),
            if self.solved(1) or self.solved(2):
                return

    def legal_moves(self):
        a0 = deepcopy(self)
        moves = []
        try:
            state = deepcopy(a0)
            state.skip_move()
            moves.append('skip')
        except InvalidMoveError:
            # print('skip')
            pass
        for i in range(4):
            for j in range(4):
                for move in ['up', 'down', 'left', 'right', 'place']:
                    try:
                        state = deepcopy(a0)
                        state.make_move(move, i, j)
                        moves.append(f'{move} {i} {j}')
                    except (InvalidMoveError, IndexError):
                        # print(move, i, j)
                        pass
        return moves

    def make_move(self, move, i, j):
        i, j = int(i), int(j)
        match move:
            case 'up':
                self.up(i, j)
            case 'down':
                self.down(i, j)
            case 'left':
                self.left(i, j)
            case 'right':
                self.right(i, j)
            case 'place':
                self.place(i, j)

    def state_tree_depth_1(self):
        states = []
        for move in self.legal_moves():
            state = deepcopy(self)
            if move == 'skip':
                state.skip_move()
            else:
                state.make_move(*move.split())
            states.append((move, state))
        return states

    def evaluate(self, jt):
        if self.h0 == 3:
            white_win, black_win = self.solved(1), self.solved(2)
            if white_win and black_win:
                return 0
            elif white_win and jt == 1 or black_win and jt == 2:
                return 1
            else:
                return 0
        return 0


if __name__ == '__main__':
    a = State()
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
                tree = a.state_tree_depth_1()
                shuffle(tree)
                chosen = max(tree, key=lambda state: state[1].evaluate(1))
                move = chosen[0]
                print(f'AI move: {move}')
                print(f'AI move value: {chosen[1].evaluate(1)}')
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
