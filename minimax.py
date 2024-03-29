import evaluators
from state import State
from random import shuffle


def minimax(state: State, depth: int, jt: int, evaluator=evaluators.win):
    if depth == 0 and state.h0 != 1 or state.h0 == 3:
        return state.evaluate(jt, evaluator=evaluator), state.last_move

    available_states = [(s[1], minimax(s[1], depth if state.h0 == 1 else depth-1, jt)) for s in state.state_tree_depth_1()]
    shuffle(available_states)
    if state.jt == jt:
        best = max(available_states, key=lambda s: s[1][0])
        return best[1][0], best[0].last_move
    elif state.jt == 3-jt:
        worst = min(available_states, key=lambda s: s[1][0])
        return worst[1][0], worst[0].last_move

