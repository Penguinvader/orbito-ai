import evaluators
from state import State
from random import shuffle


def minimax(state: State, depth: int, jt: int, evaluator=evaluators.win):
    if depth == 0 and state.h0 != 1 or state.h0 == 3:
        return state.evaluate(jt, evaluator=evaluator), state.last_move

    child_nodes = [(s[1], minimax(s[1], depth if state.h0 == 1 else depth - 1, jt)) for s in
                   state.child_nodes()]
    shuffle(child_nodes)
    if state.jt == jt:
        best = max(child_nodes, key=lambda s: s[1][0])
        return best[1][0], best[0].last_move
    elif state.jt == 3 - jt:
        worst = min(child_nodes, key=lambda s: s[1][0])
        return worst[1][0], worst[0].last_move


def minimax_ab(state: State, depth: int, jt: int, alpha=(-1000.0, 'alpha'), beta=(1000, 'beta'),
               evaluator=evaluators.win):
    return alpha_beta(state, depth, jt, alpha, beta, evaluator=evaluator)


def alpha_beta(state: State, depth: int, jt: int, alpha, beta, evaluator=evaluators.win):
    if depth == 0 and state.h0 != 1 or state.h0 == 3:
        return state.evaluate(jt, evaluator=evaluator), state.last_move

    child_nodes = state.child_nodes()
    shuffle(child_nodes)
    if state.jt == jt:
        best_val = -1000.0, 'default max'
        for node in child_nodes:
            value = alpha_beta(node[1], depth - 1, jt, alpha, beta, evaluator)
            best_val = max(value, best_val, key=lambda n: n[0])
            alpha = max(alpha, best_val, key=lambda n: n[0])
            if beta[0] <= alpha[0]:
                break
        return best_val
    elif state.jt == 3 - jt:
        worst_val = 1000.0, 'default min'
        for node in child_nodes:
            value = alpha_beta(node[1], depth - 1, jt, alpha, beta, evaluator)
            worst_val = min(value, worst_val, key=lambda n: n[0])
            beta = min(alpha, worst_val, key=lambda n: n[0])
            if beta[0] <= alpha[0]:
                break
        return worst_val
