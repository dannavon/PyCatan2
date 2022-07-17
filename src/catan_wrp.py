
from pycatan import Game, DevelopmentCard, Resource
from pycatan.board import BeginnerBoard, BoardRenderer, BuildingType
import string
import random
import sys
from copy import deepcopy

class Catan(object):
    def __init__(self):

        self.game = Game(BeginnerBoard())
        self.renderer = BoardRenderer(self.game.board)
        self.label_letters = string.ascii_lowercase + string.ascii_uppercase + "123456789"

        self.picking_stage = True

        player_order = list(range(len(self.game.players)))
        for i in player_order + list(reversed(player_order)):
            current_player = self.game.players[i]
            print("Player %d, it is your turn!" % (i + 1))
            coords = self.choose_intersection(self.game.board.get_valid_settlement_coords(current_player, ensure_connected=False),
                                         "Where do you want to build your settlement? ")
            self.game.build_settlement(player=current_player, coords=coords, cost_resources=False, ensure_connected=False)
            current_player.add_resources(self.game.board.get_hex_resources_for_intersection(coords))
            # Print the road options
            road_options = self.game.board.get_valid_road_coords(current_player, connected_intersection=coords)
            road_coords = self.choose_path(road_options, "Where do you want to build your road to? ")
            self.game.build_road(player=current_player, path_coords=road_coords, cost_resources=False)

        self.cur_id_player = 0
        self.current_player = self.game.players[self.cur_id_player]

        # Roll the dice
        self.dice = self.roll_dice()

    def choose_intersection(self, intersection_coords, prompt):
        # Label all the letters on the board
        intersection_list = [self.game.board.intersections[i] for i in intersection_coords]
        intersection_list.sort(key=lambda i: self.get_coord_sort_by_xy(i.coords))
        intersection_labels = {intersection_list[i]: self.label_letters[i] for i in range(len(intersection_list))}
        self.renderer.render_board(intersection_labels=intersection_labels)
        # Prompt the user
        letter = input(prompt)
        letter_to_intersection = {v: k for k, v in intersection_labels.items()}
        intersection = letter_to_intersection[letter]
        return intersection.coords

    def get_coord_sort_by_xy(self, c):
        x, y = self.renderer.get_coords_as_xy(c)
        return 1000 * x + y

    def choose_path(self, path_coords, prompt):
        # Label all the paths with a letter
        path_list = [self.game.board.paths[i] for i in path_coords]
        path_labels = {path_list[i]: self.label_letters[i] for i in range(len(path_coords))}
        self.renderer.render_board(path_labels=path_labels)
        # Ask the user for a letter
        letter = input(prompt)[0]
        # Get the path from the letter entered by the user
        letter_to_path = {v: k for k, v in path_labels.items()}
        return letter_to_path[letter].path_coords

    def choose_hex(self, hex_coords, prompt):
        # Label all the hexes with a letter
        hex_list = [self.game.board.hexes[i] for i in hex_coords]
        hex_list.sort(key=lambda h: self.get_coord_sort_by_xy(h.coords))
        hex_labels = {hex_list[i]: self.label_letters[i] for i in range(len(hex_list))}
        self.renderer.render_board(hex_labels=hex_labels)
        letter = input(prompt)
        letter_to_hex = {v: k for k, v in hex_labels.items()}
        return letter_to_hex[letter].coords

    def choose_resource(self, prompt):
        print(prompt)
        resources = [res for res in Resource]
        for i in range(len(resources)):
            print("%d: %s" % (i, resources[i]))
        resource_choice = int(input('->  '))
        return resources[resource_choice]

    def move_robber(self, player):
        # Don't let the player move the robber back onto the same hex
        hex_coords = self.choose_hex([c for c in self.game.board.hexes if c != self.game.board.robber],
                                "Where do you want to move the robber? ")
        self.game.board.robber = hex_coords
        # Choose a player to steal a card from
        potential_players = list(self.game.board.get_players_on_hex(hex_coords))
        print("Choose who you want to steal from:")
        for p in potential_players:
            i = self.game.players.index(p)
            print("%d: Player %d" % (i + 1, i + 1))
        p = int(input('->  ')) - 1
        # If they try and steal from another player they lose their chance to steal
        to_steal_from = self.game.players[p] if self.game.players[p] in potential_players else None
        if to_steal_from:
            resource = to_steal_from.get_random_resource()
            player.add_resources({resource: 1})
            to_steal_from.remove_resources({resource: 1})
            print("Stole 1 %s for player %d" % (resource, p + 1))

    def roll_dice(self):
        dice = random.randint(1, 6) + random.randint(1, 6)
        if dice == 7:
            # TBA
            pass
        else:
            self.game.add_yield_for_roll(dice)

        self.dice = dice
        return dice

    def end_turn(self):
        self.cur_id_player = (self.cur_id_player + 1) % len(self.game.players)
        self.current_player = self.game.players[self.cur_id_player]

        self.roll_dice()

    def set_state(self, state):
        """change the state of the game to the given state"""
        self.game = state[0]
        self.renderer = BoardRenderer(self.game.board)

        self.cur_id_player = state[1]
        self.current_player = self.game.players[self.cur_id_player]

        self.dice = state[2]


    def get_state(self):
        return (deepcopy(self.game), self.cur_id_player, self.dice)

    def get_actions(self):
        """return a list of all the actions"""
        available_actions = [(4,)]
        possible_trades = list(self.current_player.get_possible_trades())
        for t in possible_trades:
            available_actions.append((3, t))

        #build city
        if self.current_player.has_resources(BuildingType.CITY.get_required_resources()):
            # Get the valid settlement coords
            valid_coords = self.game.board.get_valid_city_coords(self.current_player)
            for c in valid_coords:
                available_actions.append((BuildingType.SETTLEMENT, c))

        #build settelement
        if self.current_player.has_resources(BuildingType.SETTLEMENT.get_required_resources()):
            # Get the valid settlement coords
            valid_coords = self.game.board.get_valid_settlement_coords(self.current_player)
            for c in valid_coords:
                available_actions.append((BuildingType.SETTLEMENT, c))

        #build road
        if self.current_player.has_resources(BuildingType.ROAD.get_required_resources()):
            # Get the valid settlement coords
            valid_coords = self.game.board.get_valid_road_coords(self.current_player)
            for c in valid_coords:
                available_actions.append((BuildingType.ROAD, c))

    def make_action(self, action):
        if action[0] == 0:
            coords = action[1]
            self.game.build_road(self.current_player, coords)

        elif action[0] == 1:
            coords = action[1]
            self.game.build_settlement(self.current_player, coords)

        elif action[0] == 2:
            coords = action[1]
            self.game.upgrade_settlement_to_city(self.current_player, coords)

        elif action[0] == 3:
            trade = action[1]
            self.current_player.add_resources(trade)

        elif action[0] == 4:
            self.end_turn()

        return self.game

catan = Catan()