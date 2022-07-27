from torch import Tensor


class Game:
    def __init__(self):
        self.state = Tensor([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        self.turn = 0

    def set_state(self, state):
        """change the state of the game to the given state"""
        self.state = state.reshape((3, 3))

    def get_state(self):
        return self.state.reshape((9,))

    def get_actions(self):
        """return a list of all the actions"""
        return [i for i in range(9) if self.state[int(i / 3), i % 3] == 0]

    def get_turn(self):
        return self.turn

    def make_action(self, action):
        """return the reward. if the game continues, return 0 for each player"""
        self.state[int(action / 3), action % 3] = self.turn + 1
        self.turn ^= 1
        for i in range(3):
            if self.state[i][0] == 1 and self.state[i][1] == 1 and self.state[i][2] == 1:
                return 1, 0
            if self.state[i][0] == 2 and self.state[i][1] == 2 and self.state[i][2] == 2:
                return 0, 1
        for j in range(3):
            if self.state[0][j] == 1 and self.state[1][j] == 1 and self.state[2][j] == 1:
                return 1, 0
            if self.state[0][j] == 2 and self.state[1][j] == 2 and self.state[2][j] == 2:
                return 0, 1
        if (self.state[0][0] == 1 and self.state[1][1] == 1 and self.state[2][2] == 1) or \
                (self.state[2][0] == 1 and self.state[1][1] == 1 and self.state[0][2] == 1):
            return 1, 0
        if (self.state[0][0] == 2 and self.state[1][1] == 2 and self.state[2][2] == 2) or \
                (self.state[2][0] == 2 and self.state[1][1] == 2 and self.state[0][2] == 2):
            return 0, 1
        return 0, 0

    def restart(self):
        self.state = Tensor([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        self.turn = 0

    def get_players_num(self):
        return 2

    def get_state_size(self):
        return 9
