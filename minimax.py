from state import State


def minimax(state: State, depth: int, jt: int, move_to_reach_this='default'):
    if depth == 0:
        return state.evaluate(jt), move_to_reach_this
    elif state.jt == jt:
        max_value = -1
        max_move = 'max default'
        for node in state.state_tree_depth_1():
            next_node = minimax(node[1], depth-1, jt, node[0])
            value = next_node[0]
            move = next_node[1]
            if value > max_value:
                max_value = value
                max_move = move
        return max_value, max_move
    elif state.jt == 3-jt:
        min_value = 1
        min_move = 'min default'
        for node in state.state_tree_depth_1():
            next_node = minimax(node[1], depth-1, jt, node[0])
            value = next_node[0]
            move = next_node[1]
            if value < min_value:
                min_value = value
                min_move = move
        return min_value, min_move


