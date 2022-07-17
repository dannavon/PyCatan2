from mcts import MCTS
from mlp import MLP
from catan_wrp import Catan


if __name__ == '__main__':
    mlp = MLP(
        in_dim=9,
        dims=[8, 16, 32, MCTS.PLAYERS_NUM],
        nonlins=['relu', 'tanh', 'relu', 'none']
    )

    mcts = MCTS(Catan(), mlp)
    print(mcts.get_best_action(50))
