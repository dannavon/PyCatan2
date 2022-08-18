import copy
import numpy as np
import torch

STATE_NODE = 0
ACTION_NODE = 1


class MCTSNode:
    def __init__(self, node_type, parent, turn):
        self.type = node_type
        self.turn = turn
        self.N = 0
        self.w = 0
        self.parent = parent
        self.sons = {}


def iteration(root, game, dnn, c, d):
    """
    make one iteration of the MCTS
    :return: void
    """

    original_state = game.get_state()
    reward, action_leaf, new_state = selection(root, game, c)
    if not game.is_over():
        action_leaf = expansion(action_leaf, new_state, game)
        reward = d * game.heuristic(new_state)
        reward += dnn.forward(new_state)
    back_propagation(action_leaf, reward)
    game.set_state(original_state)


def selection(root, game, c):
    """
    :param root: the root of the MCTS
    :param game: the game simulator in initial state
    :param c: the exploration exploitation factor
    :return: reward, leaf, new_state, where the leaf is an action node, the new_state is the state node that is not
    in the tree yet, and the reward is the given reward of playing the leaf action.
    if the reward is not None, then the new_state is None because it's the end of the game.
    """
    reward = [0] * game.get_players_num()

    while True:
        if root.type == STATE_NODE:
            best_action = None
            best_action_uct = -np.inf
            for action in root.sons:
                action_node = root.sons[action]
                if action_node.N == 0:
                    uct = np.inf
                else:
                    uct = action_node.w / action_node.N + c * np.sqrt(np.log(root.N) / action_node.N)
                if uct > best_action_uct:
                    best_action_uct = uct
                    best_action = action
            root = root.sons[best_action]
            reward = game.make_action(tuple(best_action))
        else:
            if not game.is_over():
                state = game.get_state()
                if tuple(np.array(state)) in root.sons:
                    root = root.sons[tuple(np.array(state))]
                else:
                    return reward, root, state
            else:
                return reward, root, None


def expansion(action_leaf, new_state, game):
    """
    :param action_leaf: a leaf of the tree
    :param new_state: the new state for insertion
    :param game: the game simulation
    :return: a random action of the new_state
    """

    new_state_node = MCTSNode(STATE_NODE, action_leaf, game.get_turn())
    action_leaf.sons[tuple(np.array(np.array(new_state)))] = new_state_node
    actions = game.get_actions()
    for action in actions:
        action_node = MCTSNode(ACTION_NODE, new_state_node, new_state_node.turn)
        new_state_node.sons[action] = action_node
    best_action = actions[0]
    return new_state_node.sons[best_action]


def back_propagation(action_leaf, reward):
    """
    :param action_leaf: the leaf of the tree
    :param reward: the reward of each player
    :return: void
    """
    node = action_leaf
    while node:
        node.N += 1
        if sum(reward) != 0:
            node.w += reward[node.turn] / sum(reward)
        node = node.parent


def mcts_get_best_action(game, dnn, c, d, iterations_num):
    """
    :param game: the game in the current state
    :param dnn: the neural network
    :param c: the exploration/exploitation factor
    :param iterations_num: the number of MCTS iterations
    :return: the most visited action after iteration_num iterations
    """

    root = MCTSNode(STATE_NODE, None, game.get_turn())
    actions = game.get_actions()

    if len(actions) == 1:
        return actions[0]

    for action in actions:
        son = MCTSNode(ACTION_NODE, root, game.get_turn())
        root.sons[action] = son

    for i in range(iterations_num):
        iteration(root, game, dnn, c, d)

    best_action = None
    biggest_w = -np.inf
    for action in root.sons:
        w = root.sons[action].w
        if w > biggest_w:
            biggest_w = w
            best_action = action
    return best_action
