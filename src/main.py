from mcts import MCTS
from mlp import MLP
from catan_wrp import Catan
import sys


if __name__ == '__main__':
    mlp = MLP(
        in_dim=158,
        dims=[8, 16, 32, MCTS.PLAYERS_NUM],
        nonlins=['relu', 'tanh', 'relu', 'none']
    )
    catan_game = Catan()
    while True:
        mcts = MCTS(catan_game, mlp)
        best_action = mcts.get_best_action(50)
        print(best_action)
        catan_game.make_action(best_action)
        if catan_game.has_ended():
            print("Congratuations! Player %d wins!" % (catan_game.get_turn + 1))
            print("Final board:")
            print(catan_game.game.board)
            sys.exit(0)


