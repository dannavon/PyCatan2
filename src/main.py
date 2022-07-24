from mcts import MCTS
from mlp import MLP
from catan_wrp import Catan


if __name__ == '__main__':
    mlp = MLP(
        in_dim=154,
        dims=[8, 16, 32, MCTS.PLAYERS_NUM],
        nonlins=['relu', 'tanh', 'relu', 'none']
    )
    catan_game = Catan()

    mcts = MCTS(catan_game, mlp)
    # catan_game.make_action(best_action)
    print("best actions:")
    print(mcts.get_best_action(50))
