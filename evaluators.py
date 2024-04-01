def uniform(state, jt):
    return 0.0


def win(state, jt):
    value = 0.0
    if state.h0 == 3:
        white_win, black_win = state.solved(1), state.solved(2)
        if white_win and black_win:
            value = 0.0
        elif white_win and jt == 1 or black_win and jt == 2:
            value = 1.0
        else:
            value = -1.0
    return value


def three_in_a_row(state, jt):
    value = win(state, jt)
    if value == 0.0:
        for row in range(4):
            for column in range(4):
                if column <= 1:
                    current, nxt, nxt2 = state.h[row][column], state.h[row][column + 1], state.h[row][column + 2]
                    if (current, nxt, nxt2) == (jt, jt, jt):
                        value += 0.1
                    elif (current, nxt, nxt2) == (3 - jt, 3 - jt, 3 - jt):
                        value -= 0.1
                if row <= 1:
                    current, nxt, nxt2 = state.h[row][column], state.h[row + 1][column], state.h[row + 2][column]
                    if (current, nxt, nxt2) == (jt, jt, jt):
                        value += 0.1
                    elif (current, nxt, nxt2) == (3 - jt, 3 - jt, 3 - jt):
                        value -= 0.1
        if (state.h[1][1] != 0 and (state.h[0][0] == state.h[1][1] == state.h[2][2]
                                    or state.h[1][1] == state.h[2][2] == state.h[3][3])):
            value += 0.1 if state.h[1][1] == jt else -0.1
        if (state.h[1][2] != 0 and (state.h[0][3] == state.h[1][2] == state.h[2][1]
                                    or state.h[1][2] == state.h[2][1] == state.h[3][0])):
            value += 0.1 if state.h[1][2] == jt else -0.1
    return value


def selfish_three(state, jt):
    value = win(state, jt)
    if value == 0.0:
        for row in range(4):
            for column in range(4):
                if column <= 1:
                    current, nxt, nxt2 = state.h[row][column], state.h[row][column + 1], state.h[row][column + 2]
                    if (current, nxt, nxt2) == (jt, jt, jt):
                        value += 0.1
                if row <= 1:
                    current, nxt, nxt2 = state.h[row][column], state.h[row + 1][column], state.h[row + 2][column]
                    if (current, nxt, nxt2) == (jt, jt, jt):
                        value += 0.1
        if (state.h[1][1] == jt and (state.h[0][0] == state.h[1][1] == state.h[2][2]
                                     or state.h[1][1] == state.h[2][2] == state.h[3][3])):
            value += 0.1
        if (state.h[1][2] == jt and (state.h[0][3] == state.h[1][2] == state.h[2][1]
                                     or state.h[1][2] == state.h[2][1] == state.h[3][0])):
            value += 0.1
    return value


def defensive_three(state, jt):
    value = win(state, jt)
    if value == 0.0:
        for row in range(4):
            for column in range(4):
                if column <= 1:
                    current, nxt, nxt2 = state.h[row][column], state.h[row][column + 1], state.h[row][column + 2]
                    if (current, nxt, nxt2) == (3 - jt, 3 - jt, 3 - jt):
                        value -= 0.1
                if row <= 1:
                    current, nxt, nxt2 = state.h[row][column], state.h[row + 1][column], state.h[row + 2][column]
                    if (current, nxt, nxt2) == (3 - jt, 3 - jt, 3 - jt):
                        value -= 0.1
        if (state.h[1][1] == 3 - jt and (state.h[0][0] == state.h[1][1] == state.h[2][2]
                                         or state.h[1][1] == state.h[2][2] == state.h[3][3])):
            value -= 0.1
        if (state.h[1][2] == 3 - jt and (state.h[0][3] == state.h[1][2] == state.h[2][1]
                                         or state.h[1][2] == state.h[2][1] == state.h[3][0])):
            value -= 0.1
    return value


def two_in_a_row(state, jt):
    value = win(state, jt)
    if value == 0.0:
        for row in range(4):
            for column in range(4):
                if column <= 2:
                    current, nxt = state.h[row][column], state.h[row][column + 1]
                    if (current, nxt) == (jt, jt):
                        value += 0.01
                    elif (current, nxt) == (3 - jt, 3 - jt):
                        value -= 0.01
                if row <= 2:
                    current, nxt = state.h[row][column], state.h[row + 1][column]
                    if (current, nxt) == (jt, jt):
                        value += 0.01
                    elif (current, nxt) == (3 - jt, 3 - jt):
                        value -= 0.01
        diags = [((0, 0), (1, 1)), ((1, 1), (2, 2)), ((2, 2), (3, 3)), ((0, 3), (1, 2)), ((1, 2), (2, 1)),
                 ((2, 1), (3, 0))]
        for diag in diags:
            current, nxt = state.h[diag[0][0]][diag[0][1]], state.h[diag[1][0]][diag[1][1]]
            if current != 0 and current == nxt:
                value += 0.01 if current == jt else -0.01

    return value
