# Installation
Our implementation is based pycatan library described below.
In order to install our project - 
```
git clone https://github.com/dannavon/PyCatan2.git
conda env update -f environment.yml
conda activate PyCatan2
```
Then you can run 
``` CatanNB.ipynb```
One can comment the <code>train_agent()</code> function.

We trained our model using Google colab using [this guide](https://medium.com/analytics-vidhya/how-to-use-google-colab-with-github-via-google-drive-68efb23a42d) 
In case training over colab is necessary paste at the beginning:
```
# %cd /content/drive/MyDrive/Git
# !git clone https://github.com/dannavon/PyCatan2.git
# %cd /content/drive/MyDrive/Git/PyCatan2
# !git pull
# !pip install colored
```

Directory structure:
* CatanNB.ipynb - main notebook that simulates the game, train and test agents.
* src:
  * catan_wrp.py - PyCatan2 wrapper, interact with the main game engine, implementing our own chosen rules
  * dataset.py - saves a game episode where each action is 'x' sample and the end results is the 'y' label.
  * main.py - a test environment for bot agents and wrapper.
  * mcts.py - Monte Carlo Tree Search implementation for multiple agents using model to predict value instead of rollouts
  * mlp.py/optimizers.py/plot.py/training.py - python files for build, train and plot the model.
* docs - explanation of the PyCatan2 library usage with examples.

rest of the files are part of the PyCatan2 library.
The reason we forked for PyCatan2 is the need of change parts of the data structure to be compatible with our needs.

This code may run on any Windows/Linux machine with Anaconda.


# pycatan

[![PyPi](https://img.shields.io/pypi/v/pycatan.svg)](https://pypi.org/project/pycatan/#description)
[![Read The Docs](https://readthedocs.org/projects/pycatan/badge)](https://pycatan.readthedocs.io/en/latest/index.html)
[![Tests](https://github.com/josefwaller/PyCatan2/actions/workflows/tests.yaml/badge.svg)](https://github.com/josefwaller/PyCatan2/actions/workflows/tests.yaml)

A python module for running games of The Settlers of Catan.

```
from pycatan import Game
from pycatan.board import RandomBoard

import random

game = Game(RandomBoard())

pOne = game.players[0]
settlement_coords = game.board.get_valid_settlement_coords(player = pOne, ensure_connected = False)
game.build_settlement(player = pOne, coords = random.choice(list(settlement_coords)), cost_resources = False, ensure_connected = False)
print(game.board)
```

produces:
```


                 3:1         2:1
                  .--'--.--'--.--'--.
                  |  5  |  2  |  6  | 2:1
               .--'--.--'--.--'--.--'--.
           2:1 | 10  |  9  |  4  |  3  |
            .--'--.--'--.--'--.--'--.--'--.
            |  8  | 11  |   R |  5  |  8  | 3:1
            '--.--'--.--s--.--'--.--'--.--'
           3:1 |  4  |  3  |  6  | 10  |
               '--.--'--.--'--.--'--.--'
                  | 11  | 12  |  9  | 3:1
                  '--.--'--.--'--.--'
                 2:1         2:1
```

**pycatan does**

* Game state (who has what resources and what buildings on what tiles)
* Gives out resources for a given roll
* Prints the board (it looks better with colour)
* Determine all the valid places to build a settlement/city/road
* Determine all the valid trades a player can do (4:1 and 2:1 with harbor)

**pycatan does not**
* Track turn order
* Handle playing development cards (though it gives you utility functions that help a lot - see the [text game tutorial on read the docs](https://pycatan.readthedocs.io/en/latest/tutorial.html#part-5-development-cards))
* Handle trades between players

PyCatan is built to be expandable. It provides all the game logic but doesn't force you to play the exact game.
It would be easy to add expansions such as a `Settlement Builder` development card or a board that is 3 tiles high and 30 tiles long.
