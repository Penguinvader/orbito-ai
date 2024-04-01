from copy import deepcopy
import numpy as np
import evaluators


class InvalidMoveError(Exception):
    pass


class State:
    rotation_matrix = np.array([[(0, 1), (0, 2), (0, 3), (1, 3)],
                                [(0, 0), (1, 2), (2, 2), (2, 3)],
                                [(1, 0), (1, 1), (2, 1), (3, 3)],
                                [(2, 0), (3, 0), (3, 1), (3, 2)]])

    def __init__(self):
        self.h0 = 2
        self.jt = 1
        self.h = np.zeros((4, 4))
        self.last_move = 'start'

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
        if self.h[i][j] == 3 - self.jt and self.h[i - 1][j] == 0 and self.h0 == 1 and i - 1 >= 0:
            self.h[i - 1][j] = self.h[i][j]
            self.h[i][j] = 0
            self.h0 = 2
            self.last_move = f'up {i} {j}'
        else:
            raise InvalidMoveError

    def down(self, i, j):
        if self.h[i][j] == 3 - self.jt and self.h[i + 1][j] == 0 and self.h0 == 1:
            self.h[i + 1][j] = self.h[i][j]
            self.h[i][j] = 0
            self.h0 = 2
            self.last_move = f'down {i} {j}'
        else:
            raise InvalidMoveError

    def left(self, i, j):
        if self.h[i][j] == 3 - self.jt and self.h[i][j - 1] == 0 and self.h0 == 1 and j - 1 >= 0:
            self.h[i][j - 1] = self.h[i][j]
            self.h[i][j] = 0
            self.h0 = 2
            self.last_move = f'left {i} {j}'
        else:
            raise InvalidMoveError

    def right(self, i, j):
        if self.h[i][j] == 3 - self.jt and self.h[i][j + 1] == 0 and self.h0 == 1:
            self.h[i][j + 1] = self.h[i][j]
            self.h[i][j] = 0
            self.h0 = 2
            self.last_move = f'right {i} {j}'
        else:
            raise InvalidMoveError

    def skip_move(self):
        if self.h0 == 1:
            self.h0 = 2
            self.last_move = f'skip'
        else:
            raise InvalidMoveError

    def place(self, i, j):
        if self.h[i][j] == 0 and self.h0 == 2:
            self.h[i][j] = self.jt
            self.rotate()
            self.h0 = 3 if self.solved(1) or self.solved(2) else 1
            self.jt = 3 - self.jt
            self.last_move = f'place {i} {j}'
        else:
            raise InvalidMoveError

    def full(self):
        self.h0 = 3
        self.last_move = f'full'
        for n in range(5):
            self.rotate()
            self.print_grid()
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

    def child_nodes(self):
        states = []
        for move in self.legal_moves():
            state = deepcopy(self)
            if move == 'skip':
                state.skip_move()
            else:
                state.make_move(*move.split())
            states.append((move, state))
        return states

    def evaluate(self, jt, evaluator=evaluators.win):
        return evaluator(self, jt)
