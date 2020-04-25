from enum import Enum
import math
import numpy
import random

MAP_SIZE = 15
MAX_TURNS = 400
NUM_PLAYERS = 4
MOVEMENT_COST = 0.1
HARVEST_RATE = 0.25


class Direction(Enum):
    NORTH = 'NORTH'
    EAST = 'EAST'
    SOUTH = 'SOUTH'
    WEST = 'WEST'
    ALL_CARDINALS = [NORTH, EAST, SOUTH, WEST]


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        self.x == other.x
        self.y == other.y

    def directional_offset(self, d: Direction):
        dx = 0
        dy = 0
        if d == Direction.NORTH.value:
            dx = 0
            dy = -1
        elif d == Direction.SOUTH.value:
            dx = 0
            dy = 1
        elif d == Direction.EAST.value:
            dx = 1
            dy = 0
        elif d == Direction.WEST.value:
            dx = -1
            dy = 0
        return Position(self.x + dx, self.y + dy)

    def normalize(self):
        x = ((self.x % MAP_SIZE) + MAP_SIZE) % MAP_SIZE
        y = ((self.y % MAP_SIZE) + MAP_SIZE) % MAP_SIZE
        return Position(x, y)

    def calculate_distance(self, target) -> int:
        normalized_source = self.normalize()
        normalized_target = target.normalize()

        dx = abs(normalized_source.x - normalized_target.x)
        dy = abs(normalized_source.y - normalized_target.y)

        toroidal_dx = min(dx, MAP_SIZE - dx)
        toroidal_dy = min(dy, MAP_SIZE - dy)

        return toroidal_dx + toroidal_dy

    @classmethod
    def from_int(cls, pos: int):
        y = math.floor(pos / MAP_SIZE)
        x = pos % MAP_SIZE
        return Position(x, y)

    def __repr__(self):
        return {"x": self.x, "y": self.y}.__repr__()


class Entity:
    def __init__(self, id: str, owner: str, position: Position):
        self.id = id
        self.owner = owner
        self.position = position

    def __eq__(self, other):
        self.id == other.id
        self.owner == other.owner
        self.position == other.position

    def __repr__(self):
        return {"id": self.id, "owner": self.owner, "position": self.position}.__repr__()


class Ship(Entity):
    def __init__(self, id: str, owner: str, position: Position, halite: float):
        super().__init__(id, owner, position)
        self.halite = halite
        self.action = None

    def move(self, direction: Direction):
        self.action = direction

    def convert(self):
        self.action = "CONVERT"

    def __repr__(self):
        return {"id": self.id, "owner": self.owner, "position": self.position,
                "halite": self.halite}.__repr__()


class Shipyard(Entity):
    def __init__(self, id: str, owner: str, position: Position):
        super().__init__(id, owner, position)
        self.action = None

    def spawn(self):
        self.action = "SPAWN"

    def __repr__(self):
        return {"id": self.id, "owner": self.owner, "position": self.position}.__repr__()


class Player:
    def __init__(self, id: str, halite: float):
        self.id = id
        self.halite = halite
        self.ships = []
        self.shipyards = []

    def add_ship(self, ship: Ship):
        self.ships.append(ship)

    def add_shipyard(self, shipyard: Shipyard):
        self.shipyards.append(shipyard)

    def __repr__(self):
        return {"id": self.id, "halite": self.halite, "ships": self.ships,
                "shipyards": self.shipyards}.__repr__()


class Cell:
    def __init__(self, position: Position, halite: float):
        self.position = position
        self.halite = halite
        self.ship = None
        self.shipyard = None

    def empty(self) -> bool:
        return self.ship is None and self.shipyard is None

    def add_ship(self, ship: Ship):
        self.ship = ship

    def add_shipyard(self, shipyard: Shipyard):
        self.shipyard = shipyard

    def __repr__(self):
        ret = {"position": self.position, "halite": self.halite}
        if self.ship is not None:
            ret["ship"] = self.ship
        if self.shipyard is not None:
            ret["shipyard"] = self.shipyard
        return ret.__repr__()


class Map:
    def __init__(self, game):
        self.game = game
        self.cells = numpy.empty((MAP_SIZE, MAP_SIZE)).tolist()

    def at(self, position: Position) -> Cell:
        normalized = position.normalize()
        return self.cells[normalized.y][normalized.x]

    def __repr__(self):
        return {"cells": self.cells}.__repr__()


class Game:
    def __init__(self, obs):
        self.turn = obs.step
        self.players = []
        self.me = None
        self.map = Map(self)

        self.init_map(obs)
        self.init_players(obs)

    def init_map(self, obs):
        for i, halite in enumerate(obs.halite):
            position = Position.from_int(i)
            cell = Cell(position, halite)
            self.map.cells[position.y][position.x] = cell

    def init_players(self, obs):
        for player_id in range(len(obs.players)):
            player_halite, shipyards, ships = obs.players[player_id]
            player = Player(player_id, player_halite)

            for ship_id, data in ships.items():
                ship_pos, ship_halite = data
                ship = Ship(ship_id, player_id, Position.from_int(ship_pos), ship_halite)
                self.map.cells[ship.position.y][ship.position.x].add_ship(ship)
                player.add_ship(ship)

            for shipyard_id, shipyard_pos in shipyards.items():
                shipyard = Shipyard(shipyard_id, player_id, Position.from_int(shipyard_pos))
                self.map.cells[shipyard.position.y][shipyard.position.x].add_shipyard(shipyard)
                player.add_shipyard(shipyard)

            self.players.append(player)

        self.me = self.players[obs.player]

    def __repr__(self):
        return {"turn": self.turn, "players": self.players, "me": self.me, "map": self.map}.__repr__()


def agent(obs):
    action = {}
    game = Game(obs)
    me = game.me

    for shipyard in me.shipyards:
        cell = game.map.at(shipyard.position)
        if me.halite >= 500 and not cell.ship:
            action[shipyard.id] = "SPAWN"

    for ship in me.ships:
        if len(me.shipyards) == 0:
            action[ship.id] = "CONVERT"
            continue

        Direction.ALL_CARDINALS.value[random.randint(0, 3)]

        max_value = 0
        next_dir = None
        current_cell = game.map.at(ship.position)
        for direction in Direction.ALL_CARDINALS.value:
            cell = game.map.at(ship.position.directional_offset(direction))
            if cell.empty() \
                    and cell.halite > max_value \
                    and cell.halite > current_cell.halite \
                    and (cell.halite * HARVEST_RATE) > (ship.halite * MOVEMENT_COST):
                max_value = cell.halite
                next_dir = direction

        if current_cell.halite < 10 and next_dir is None:
            next_dir = Direction.ALL_CARDINALS.value[random.randint(0, 3)]

        if next_dir is not None:
            action[ship.id] = next_dir

    return action


# For debugging
# from kaggle_environments import make
#
# env = make("halite", debug=True)
# trainer = env.train([None, "random"])
# observation = trainer.reset()
#
# while not env.done:
#     my_action = agent(observation)
#     print("My Action", my_action)
#     observation, reward, done, info = trainer.step(my_action)
