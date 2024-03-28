from state import State


def minimax(state: State, depth: int, jt: int):
    if depth == 0 or state.h0 == 3:
        return state.evaluate(jt), state.last_move

    available_states = [(s[1], minimax(s[1], depth-1, jt)) for s in state.state_tree_depth_1()]

    if state.jt == jt:
        best = max(available_states, key=lambda s: s[1][0])
        return best[1][0], best[0].last_move
    elif state.jt == 3-jt:
        worst = min(available_states, key=lambda s: s[1][0])
        return worst[1][0], worst[0].last_move

