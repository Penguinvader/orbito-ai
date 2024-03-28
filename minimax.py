from state import State


def minimax(state: State, depth: int, jt: int):
    if depth == 0 or state.h0 == 3:
        return state.evaluate(jt), 'end'

    available_states = [s[1] for s in state.state_tree_depth_1()]

    if state.jt == jt:
        best_state = max(available_states, key=lambda s: minimax(s, depth-1, jt)[0])
        return best_state.evaluate(jt), best_state.last_move
    elif state.jt == 3-jt:
        worst_state = min(available_states, key=lambda s: minimax(s, depth - 1, jt)[0])
        return worst_state.evaluate(jt), worst_state.last_move

