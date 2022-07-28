import numpy as np

from pycatan import Game, DevelopmentCard, Resource
from pycatan.board import BeginnerBoard, BoardRenderer, BuildingType, Coords, IntersectionBuilding, PathBuilding
import string
import random
from torch import Tensor
import sys
from copy import deepcopy


class Catan(object):
    def __init__(self):

        self.picked_settl_coo = None
        self.game = Game(BeginnerBoard())
        self.renderer = BoardRenderer(self.game.board)
        self.label_letters = string.ascii_lowercase + string.ascii_uppercase + "123456789"

        player_order = list(range(len(self.game.players)))
        self.player_order = [0] + player_order + list(reversed(player_order))  # [0] designated for the last pop

        self.cur_id_player = self.player_order.pop()
        self.current_player = self.game.players[self.cur_id_player]

        # Roll the dice
        self.dice = self.roll_dice()

    def get_players_num(self):
        return len(self.game.players)

    def get_state_size(self):
        return 158

    def restart(self):
        return self.__class__()

    def get_turn(self):
        return self.cur_id_player

    def choose_intersection(self, intersection_coords, prompt):
        # Label all the letters on the board
        intersection_list = [self.game.board.intersections[i] for i in intersection_coords]
        intersection_list.sort(key=lambda i: self.get_coord_sort_by_xy(i.coords))
        intersection_labels = {intersection_list[i]: self.label_letters[i] for i in range(len(intersection_list))}
        self.renderer.render_board(intersection_labels=intersection_labels)
        # Prompt the user
        # letter = input(prompt)
        letter = random.choice(list(intersection_labels.values()))
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
        # letter = input(prompt)[0]
        letter = random.choice(list(path_labels.values()))
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
        # for i in range(len(resources)):
        #     print("%d: %s" % (i, resources[i]))
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

        self.cur_id_player = state[0]
        self.current_player = self.game.players[self.cur_id_player]

        self.dice = state[1]
        # self.game.largest_army_owner = state[2]
        if state[2] == 0:
            self.game.longest_road_owner = None
        else:
            self.game.longest_road_owner = self.current_player(state[2]-1)

        i = 3
        for k, v in self.game.board.intersections.items():
            if state[i] != 0:
                player = self.game.players[state[i] / 10]
                type = state[i] % 10
                if self.game.board.intersections[k].building != None:
                    self.game.board.intersections[k].building.owner = player
                    self.game.board.intersections[k].building.building_type = type
                else:
                    self.game.board.intersections[k].building = IntersectionBuilding(player, type, k)
            i += 1

        for k, v in self.game.board.paths.items():
            if state[i] != 0:
                player = self.game.players[state[i] / 10]
                if self.game.board.paths[k].building is not None:
                    self.game.board.paths[k].building.owner = player
                    self.game.board.paths[k].building.building_type = type
                else:
                    self.game.board.paths[k].building = PathBuilding(player, BuildingType.ROAD, k)
            i += 1

        for p in self.game.players:
            for r, n in p.resources.items():
                p.resources[r] = state[i]
                i += 1

            if len(p.connected_harbors) == state[i]:
                i += len(p.connected_harbors)*4+1
                continue
            else:
                coords = set({Coords(state[i],state[i+1]), Coords(state[i+2],state[i+3])})
                for harbor in self.harbors.values():
                    if coords in harbor.path_coords and harbor not in p.connected_harbors:
                        p.connected_harbors.add(harbor)

        self.renderer = BoardRenderer(self.game.board)

    def get_state(self):
        # serialize game -
        # serialize board:
        #       hexes: coodrs,type,token
        #       harbors: path_coords(2coords),resource
        #       intersections
        #       paths
        # serialize players:
        #     resources: Dict[Resource, int]
        #     development_cards?
        #     connected_harbors = set()
        #     number_played_knights?
        # largest army/road(/carddeck?)

        # serialize id and dice

        s = np.array([], dtype=np.float)  # state representation.
        s = np.append(s, self.cur_id_player)
        s = np.append(s, self.dice)
        # s = np.append(s, self.game.largest_army_owner)
        if self.game.longest_road_owner is not None:
            a = self.game.longest_road_owner.id + 1
        else:
            a = 0
        s = np.append(s, a)
        # s = np.append(s, self.game.development_card_deck)
        # serialize board:
        #   hexes:
        # hexes = [[h.coords.q, h.coords.r, h.hex_type, h.token_number] for h in self.game.board.hexes.values()]
        # s = np.append(s, hexes)
        #   harbors:
        # harbors = []
        # for h, r in self.game.board.harbors.items():
        #     for v in h:
        #         harbors.append(v.q)
        #         harbors.append(v.r)
        #     harbors.append(r.resource)
        # s = np.append(s, harbors)

        #   intersections:
        # intersections = [[i.coords.q, i.coords.r, i.building] for i in self.game.board.intersections.values()]
        for i in self.game.board.intersections.values():
            structure_type = 0
            if i.building is not None:
                structure_type = i.building.owner.id*10+i.building.building_type.value
            s = np.append(s, structure_type)

        #   paths:
        # paths = [b.building.owner for h, b in self.game.board.paths.items()]

        for h, b in self.game.board.paths.items():
            structure_type = 0
            if b.building is not None:
                structure_type = b.building.owner.id * 10 + 1
            s = np.append(s, structure_type)

        # robber = [self.game.board.robber.q, self.game.board.robber.r]
        # s = np.append(s, robber)

        for p in self.game.players:
            resources = [n for r, n in p.resources.items()]
            s = np.append(s, resources)

            # connected_harbors = [len(p.connected_harbors)]
            # for h in p.connected_harbors:
            #     for v in h:
            #         connected_harbors.append(v.q)
            #         connected_harbors.append(v.r)
            # s = np.append(s, connected_harbors)

            # development_cards = [[r.value,n] for r,n in p.development_cards.items()]
            # s = np.append(s, development_cards)
            # s = np.append(s, p.number_played_knights)

        # Connect the player to a harbor if they can

        for c, h in self.game.board.harbors.items():
            h_assigned_to = 0
            for i, p in enumerate(self.game.players):
                if c in p.connected_harbors:
                    h_assigned_to = i+1
                    continue
            s = np.append(s, h_assigned_to)

        return Tensor(np.array(s, dtype=np.float))

    def get_actions(self):
        """return a list of all the actions"""
        available_actions = []
        if len(self.player_order) > 0:
            if self.picked_settl_coo is None:
                valid_coords = self.game.board.get_valid_settlement_coords(self.current_player, ensure_connected=False)
                for c in valid_coords:
                    available_actions.append((BuildingType.SETTLEMENT, c))
            else:
                road_options = self.game.board.get_valid_road_coords(self.current_player,
                                                                     connected_intersection=self.picked_settl_coo)
                for r in road_options:
                    available_actions.append((BuildingType.ROAD, r))

        else:
            available_actions.append((4,))  # end turn
            possible_trades = list(self.current_player.get_possible_trades())
            for t in possible_trades:
                available_actions.append((3, tuple(t.items())))

            # build city
            if self.current_player.has_resources(BuildingType.CITY.get_required_resources()):
                # Get the valid city coords
                valid_coords = self.game.board.get_valid_city_coords(self.current_player)
                for c in valid_coords:
                    available_actions.append((BuildingType.CITY, c))

            # build settlement
            if self.current_player.has_resources(BuildingType.SETTLEMENT.get_required_resources()):
                # Get the valid settlement coords
                valid_coords = self.game.board.get_valid_settlement_coords(self.current_player)
                for c in valid_coords:
                    available_actions.append((BuildingType.SETTLEMENT, c))

            # build road
            if self.current_player.has_resources(BuildingType.ROAD.get_required_resources()):
                # Get the valid road coords
                valid_coords = self.game.board.get_valid_road_coords(self.current_player)
                for c in valid_coords:
                    available_actions.append((BuildingType.ROAD, c))

        return available_actions

    def make_action(self, action):
        initialization_stage = len(self.player_order) > 0
        if hasattr(action[0], 'value'):
            a = action[0].value
        else:
            a = action[0]

        if a == 0:  # road
            coords = action[1]
            self.game.build_road(self.current_player, coords, cost_resources=(not initialization_stage))
            if initialization_stage:
                self.picked_settl_coo = None
                self.cur_id_player = self.player_order.pop()
                self.current_player = self.game.players[self.cur_id_player]

        elif a == 1:  # settlement
            coords = action[1]
            self.game.build_settlement(self.current_player, coords, ensure_connected=(not initialization_stage),
                                       cost_resources=(not initialization_stage))
            if initialization_stage:
                self.picked_settl_coo = coords
                if len(self.player_order) <= len(self.game.players) + 1:
                    self.current_player.add_resources(self.game.board.get_hex_resources_for_intersection(coords))

        elif a == 2:
            coords = action[1]
            self.game.upgrade_settlement_to_city(self.current_player, coords)

        elif a == 3:
            trade = dict(action[1])
            self.current_player.add_resources(trade)

        elif a == 4:
            self.end_turn()

        reward = [0, 0, 0, 0]

        if self.game.get_victory_points(self.current_player) >= 10:
            print("Congratulations! Player %d wins!" % (self.cur_id_player + 1))
            print("Final board:")
            print(self.game.board)
            players = self.game.players
            reward = [self.game.get_victory_points(p) for p in players]
        return Tensor(reward)

    def has_ended(self):
        return self.game.get_victory_points(self.current_player) >= 10


