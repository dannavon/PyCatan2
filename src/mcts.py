import copy
import numpy as np


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


def iteration(root, original_game, dnn, c):
    """
    make one iteration of the MCTS
    :return: void
    """
    game = copy.deepcopy(original_game)
    reward, action_leaf, new_state = selection(root, game, c)
    if sum(reward) == 0:
        action_leaf = expansion(action_leaf, new_state, game)
        reward = dnn.forward(new_state)
    back_propagation(action_leaf, reward)


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
            reward = game.make_action(best_action)
        else:
            if sum(reward) == 0:
                state = game.get_state()
                if tuple(state) in root.sons:
                    root = root.sons[tuple(state)]
                else:
                    return [0] * game.get_players_num(), root, state
            else:
                return reward, root, None


def expansion(action_leaf, new_state, game):
    """
    :param action_leaf: a leaf of the tree
    :param new_state: the new state for insertion
    :param game: the game simulation
    :return: a random action of the new_state
    """

    new_state_node = MCTSNode(STATE_NODE, action_leaf, (action_leaf.turn + 1) % game.get_players_num())
    action_leaf.sons[tuple(new_state)] = new_state_node
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


def mcts_get_best_action(game, dnn, c, iterations_num):
    """
    :param game: the game in the current state
    :param dnn: the neural network
    :param c: the exploration/exploitation factor
    :param iterations_num: the number of MCTS iterations
    :return: the most visited action after iteration_num iterations
    """

    root = MCTSNode(STATE_NODE, None, 0)
    actions = game.get_actions()
    for action in actions:
        son = MCTSNode(ACTION_NODE, root, 0)
        root.sons[action] = son

    for i in range(iterations_num):
        iteration(root, game, dnn, c)

    best_action = None
    biggest_visits_num = -1
    for action in root.sons:
        visits_num = root.sons[action].N
        if visits_num > biggest_visits_num:
            biggest_visits_num = visits_num
            best_action = action
    return best_action


# class MCTS:
#     C = 0.1
#     PLAYERS_NUM = 2
#
#     def __init__(self, game, dnn):
#         self.original_game = game
#         self.game = copy.deepcopy(self.original_game)
#         self.dnn = dnn
#         self.root = MCTSNode(STATE_NODE, None, 0)
#         actions = self.game.get_actions()
#         for action in actions:
#             son = MCTSNode(ACTION_NODE, self.root, 0)
#             self.root.sons[action] = son
#
#     def get_best_action(self, iterations_num):
#         """
#         :param iterations_num: the number of MCTS iterations
#         :return: the most visited action after iteration_num iterations
#         """
#
#         for i in range(iterations_num):
#             self.iteration()
#         best_action = None
#         biggest_visits_num = -1
#         for action in self.root.sons:
#             visits_num = self.root.sons[action].N
#             if visits_num > biggest_visits_num:
#                 biggest_visits_num = visits_num
#                 best_action = action
#         return best_action
#
#     def iteration(self):
#         """
#         make one iteration of the MCTS
#         :return: void
#         """
#         self.game = copy.deepcopy(self.original_game)
#         reward, action_leaf, new_state = self.selection(self.root, self.game)
#         if sum(reward) == 0:
#             action_leaf = self.expansion(action_leaf, new_state, self.game)
#             reward = self.dnn.forward(new_state)
#         self.back_propagation(action_leaf, reward)
#
#     @staticmethod
#     def selection(root, game):
#         """
#         :param root: the root of the MCTS
#         :param game: the game simulator in initial state
#         :return: reward, leaf, new_state, where the leaf is an action node, the new_state is the state node that is not
#         in the tree yet, and the reward is the given reward of playing the leaf action.
#         if the reward is not None, then the new_state is None because it's the end of the game.
#         """
#         reward = [0] * MCTS.PLAYERS_NUM
#
#         while True:
#             if root.type == STATE_NODE:
#                 best_action = None
#                 best_action_uct = -np.inf
#                 for action in root.sons:
#                     action_node = root.sons[action]
#                     if action_node.N == 0:
#                         uct = np.inf
#                     else:
#                         uct = action_node.w / action_node.N + MCTS.C * np.sqrt(np.log(root.N) / action_node.N)
#                     if uct > best_action_uct:
#                         best_action_uct = uct
#                         best_action = action
#                 root = root.sons[best_action]
#                 reward = game.make_action(best_action)
#             else:
#                 if sum(reward) == 0:
#                     state = game.get_state()
#                     if tuple(state) in root.sons:
#                         root = root.sons[tuple(state)]
#                     else:
#                         return [0] * MCTS.PLAYERS_NUM, root, state
#                 else:
#                     return reward, root, None
#
#     @staticmethod
#     def expansion(action_leaf, new_state, game):
#         """
#         :param action_leaf: a leaf of the tree
#         :param new_state: the new state for insertion
#         :param game: the game simulation
#         :return: a random action of the new_state
#         """
#
#         new_state_node = MCTSNode(STATE_NODE, action_leaf, (action_leaf.turn + 1) % MCTS.PLAYERS_NUM)
#         action_leaf.sons[tuple(new_state)] = new_state_node
#         actions = game.get_actions()
#         for action in actions:
#             action_node = MCTSNode(ACTION_NODE, new_state_node, new_state_node.turn)
#             new_state_node.sons[action] = action_node
#         best_action = actions[0]
#         return new_state_node.sons[best_action]
#
#     @staticmethod
#     def back_propagation(action_leaf, reward):
#         """
#         :param action_leaf: the leaf of the tree
#         :param reward: the reward of each player
#         :return: void
#         """
#         node = action_leaf
#         while node:
#             node.N += 1
#             if sum(reward) != 0:
#                 node.w += reward[node.turn] / sum(reward)
#             node = node.parent
