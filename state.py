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
    moves = ('skip', 'full',
             'place 0 0', 'place 0 1', 'place 0 2', 'place 0 3',
             'place 1 0', 'place 1 1', 'place 1 2', 'place 1 3',
             'place 2 0', 'place 2 1', 'place 2 2', 'place 2 3',
             'place 3 0', 'place 3 1', 'place 3 2', 'place 3 3',
             'up 1 0', 'up 1 1', 'up 1 2', 'up 1 3',
             'up 2 0', 'up 2 1', 'up 2 2', 'up 2 3',
             'up 3 0', 'up 3 1', 'up 3 2', 'up 3 3',
             'down 0 0', 'down 0 1', 'down 0 2', 'down 0 3',
             'down 1 0', 'down 1 1', 'down 1 2', 'down 1 3',
             'down 2 0', 'down 2 1', 'down 2 2', 'down 2 3',
             'left 0 1', 'left 0 2', 'left 0 3',
             'left 1 1', 'left 1 2', 'left 1 3',
             'left 2 1', 'left 2 2', 'left 2 3',
             'left 3 1', 'left 3 2', 'left 3 3',
             'right 0 0', 'right 0 1', 'right 0 2',
             'right 1 0', 'right 1 1', 'right 1 2',
             'right 2 0', 'right 2 1', 'right 2 2',
             'right 3 0', 'right 3 1', 'right 3 2'
             )

    def __init__(self):
        self.h0 = 2
        self.jt = 1
        self.h = np.zeros((4, 4))
        self.last_move = 'start'

    def print_grid(self):
        for row in self.h:
            print("".join("⚪" if j == 1 else "⚫" if j == 2 else "⭕" for j in row))

    def constraint(self):
        white_count = sum(row.count(1) for row in self.h)
        black_count = sum(row.count(2) for row in self.h)
        return (self.jt == 1 and white_count == black_count) or (self.jt == 2 and white_count == black_count + 1)

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
        rotated = np.array([[self.h[col[0]][col[1]] for col in row] for row in self.rotation_matrix])
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
        if self.h0 == 1 and 0 in [n for row in self.h for n in row]:
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
        if 0 not in [n for row in self.h for n in row] and self.h0 == 1:
            self.h0 = 3
            self.last_move = f'full'
            for n in range(5):
                self.rotate()
                if self.solved(1) or self.solved(2):
                    return
        else:
            raise InvalidMoveError

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
        try:
            state = deepcopy(a0)
            state.full()
            moves.append('full')
        except InvalidMoveError:
            # print('full')
            pass
        for i in range(4):
            for j in range(4):
                for move in ['up', 'down', 'left', 'right', 'place']:
                    try:
                        state = deepcopy(a0)
                        state.make_move_inside(move, i, j)
                        moves.append(f'{move} {i} {j}')
                    except (InvalidMoveError, IndexError):
                        # print(move, i, j)
                        pass
        return moves

    def legal_moves_numeric(self):
        legal = self.legal_moves()
        possible_moves = np.array([1 if move in legal else 0 for move in self.moves])
        # possible_moves[0] = 0 if 1 in possible_moves[1:] else 1
        return possible_moves

    def make_move(self, move_id):
        self.make_move_text(self.moves[move_id])

    def make_move_text(self, move):
        if move == 'skip':
            self.skip_move()
        elif move == 'full':
            self.full()
        else:
            self.make_move_inside(*move.split())

    def make_move_inside(self, move, i, j):
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
            state.make_move_text(move)
            states.append((move, state))
        return states

    def evaluate(self, jt, evaluator=evaluators.win):
        return evaluator(self, jt)

    def get_encoded_state(self):
        h0_map = np.repeat(self.h0, 16).reshape((4, 4))
        jt_map = np.repeat(self.jt, 16).reshape((4, 4))
        encoded_state = np.stack(
            (h0_map == 1, jt_map == 1, self.h == 2, self.h == 0, self.h == 1)
        ).astype(np.float32)

        return encoded_state
