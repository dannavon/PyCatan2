import os.path

import matplotlib.pyplot as plt
from mcts import mcts_get_best_action
from mlp import MLP
from game import Game
from catan_wrp import Catan
import sys
from dataset import Dataset
import torch
from torch import Tensor
from training import MLPTrainer
import torch.nn.functional
from plot import plot_fit


hp_model_training = dict(loss_fn=torch.nn.MSELoss(),
                         batch_size=100,
                         num_epochs=100,
                         test_ratio=0.2,
                         valid_ratio=0.2,
                         early_stopping=100)

hp_optimizer = dict(lr=0.001,
                    weight_decay=0.01,
                    momentum=0.99)

hp_model = dict(hidden_layers_num=1,
                hidden_layers_size=20,
                activation='relu')

hp_mcts = dict(c=1,
               d=3,
               iterations_num=500)

hp_agent_training = dict(games_num=100)


def create_demo_data_loaders():
    dataset = Dataset(hp_model_training['batch_size'], hp_model_training['valid_ratio'], hp_model_training['test_ratio'])

    for game_num in range(10):
        for trains_num in range(1 + game_num):
            dataset.add_sample(torch.rand(9))
        dataset.set_label(Tensor((game_num + 0.1, game_num + 1.1)))

    return dataset.get_data_loaders()


def create_model(in_dim, out_dim, model_file):
    if os.path.isfile(model_file):
        print(f'loading model from "{model_file}"...')
        mlp = torch.load(model_file)
        print(mlp)
        return mlp

    mlp = MLP(
        in_dim=in_dim,
        dims=[hp_model['hidden_layers_size']] * hp_model['hidden_layers_num'] + [out_dim],
        nonlins=[hp_model['activation']] * hp_model['hidden_layers_num'] + ['none']
    )

    print('creating model...')
    print(mlp)
    return mlp


def train(dl_train, dl_valid, dl_test, model):
    loss_fn = hp_model_training['loss_fn']
    optimizer = torch.optim.SGD(params=model.parameters(), **hp_optimizer)
    trainer = MLPTrainer(model, loss_fn, optimizer)

    return trainer.fit(dl_train,
                       dl_valid,
                       num_epochs=hp_model_training['num_epochs'],
                       print_every=10,
                       early_stopping=hp_model_training['early_stopping'])


def mlp_test():
    GAME_STATE_SIZE = 9
    NUMBER_OF_PLAYERS = 2
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(device)
    plt.rcParams.update({'font.size': 12})

    dl_train, dl_valid, dl_test = create_demo_data_loaders()

    model = create_model(GAME_STATE_SIZE, NUMBER_OF_PLAYERS, 'model')

    fit_res = train(dl_train, dl_valid, dl_test, model)

    plot_fit(fit_res, log_loss=False, train_test_overlay=True)

    plt.show()


def mcts_test():
    game = Game()
    model = create_model(game.get_state_size(), game.get_players_num(), 'model')
    print(mcts_get_best_action(game, model, hp_mcts['c'], hp_mcts['d'], hp_mcts['iterations_num']))


def train_agent(games_num, model_path):
    model = create_model(Catan.get_state_size(), Catan.get_players_num(), model_path)

    for i in range(1, games_num + 1):
        print(f'_________________game {i}/{games_num}________________')

        catan_game = Catan()

        ds = Dataset(hp_model_training['batch_size'], hp_model_training['valid_ratio'], hp_model_training['test_ratio'])

        turns_num = 0

        while True:
            turns_num += 1

            best_action = mcts_get_best_action(catan_game, model, hp_mcts['c'], hp_mcts['d'], hp_mcts['iterations_num'])
            print("Player " + str(catan_game.get_turn() + 1) + ", action:" + str(best_action))

            reward = catan_game.make_action(best_action)
            if best_action[0] == 4:
                print("Player " + str(catan_game.get_turn() + 1) + " turn!, dice: " + str(catan_game.dice))
                # print(catan_game.game.board)

            ds.add_sample(catan_game.get_state())
            if catan_game.is_over():
                print("Congratulations! Player %d wins!" % (catan_game.cur_id_player + 1))
                print("Final board:")
                print(catan_game.game.board)
                ds.set_label(reward)

                dl_train, dl_valid, dl_test = ds.get_data_loaders()
                fit_res = train(dl_train, dl_valid, dl_test, model)
                plot_fit(fit_res, log_loss=False, train_test_overlay=True)
                plt.show()
                print(ds)

                print(f'saving model in "{model_path}"')
                torch.save(model, model_path)
                break


if __name__ == '__main__':
    train_agent(100, 'model')
