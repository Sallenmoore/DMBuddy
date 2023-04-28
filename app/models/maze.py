import itertools
import json
import random
import sys

from autonomous import log
from autonomous.model.automodel import AutoModel


class Cell(object):
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.connected = False
        self.connectedTo = []
        self.room = None

    def connect(self, other):
        self.connectedTo.append(other)
        other.connectedTo.append(self)
        self.connected = True
        other.connected = True

    def __str__(self):
        return "(%i,%i)" % (self.x, self.y)


class Maze(AutoModel):
    """A Maze, represented as a grid of cells."""

    # set model default attributes
    attributes = {
        "name": "",
        "cols": None,
        "rows": None,
        "wall_img": "",
        "floor_img": "",
    }

    def __init__(self, rows, cols=None, num_rooms=None, name="Dungeon"):
        """Initialize the maze grid.
        The maze consists of nx x ny cells and will be constructed starting
        at the cell indexed at (ix, iy).

        """
        self.name = name
        self.rows = rows
        self.cols = cols if cols else rows
        self.room_size = cols if cols else rows
        self.cells = {}

    def __str__(self):
        """Return a (crude) string representation of the maze."""
        maze = ""
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) in self.cells:
                    maze += " "
                else:
                    maze += "#"
        return maze

    def generate(self):
        # 1. Divide the map into a grid of evenly sized cells.
        for y in range(self.cols):
            for x in range(self.rows):
                c = Cell(x, y, len(self.cells))
                self.cells[(c.x, c.y)] = c

        # 2. Pick a random cell as the current cell and mark it as connected.
        current = lastCell = firstCell = random.choice(list(self.cells.values()))
        current.connected = True

        while True:
            unconnected = list(
                filter(lambda x: not x.connected, self.getNeighborCells(current))
            )
            if not unconnected:
                break

            # 3a. Connect to one of them.
            neighbor = random.choice(unconnected)
            current.connect(neighbor)

            # 3b. Make that cell the current cell.
            current = lastCell = neighbor

        # 4. While there are unconnected cells:
        while True:
            unconnected = list(filter(lambda x: not x.connected, self.cells.values()))
            if not unconnected:
                break

            # 4a. Pick a random connected cell with unconnected neighbors and connect to one of them.
            candidates = []
            for cell in filter(lambda x: x.connected, self.cells.values()):
                neighbors = list(
                    filter(lambda x: not x.connected, self.getNeighborCells(cell))
                )
                if not neighbors:
                    continue
                candidates.append((cell, neighbors))
            if candidates:
                cell, neighbors = random.choice(candidates)
                cell.connect(random.choice(neighbors))

        # 5. Pick 0 or more pairs of adjacent cells that are not connected and connect them.
        extraConnections = random.randint(
            int((self.rows + self.cols) / 4), int((self.rows + self.cols) / 1.2)
        )
        maxRetries = 10
        while extraConnections > 0 and maxRetries > 0:
            cell = random.choice(list(self.cells.values()))
            neighbor = random.choice(list(self.getNeighborCells(cell)))
            if cell in neighbor.connectedTo:
                maxRetries -= 1
                continue
            cell.connect(neighbor)
            extraConnections -= 1

        # 6. Within each cell, create a room of random shape
        rooms = []
        for cell in self.cells.values():
            width = random.randint(3, self.room_size - 2)
            height = random.randint(3, self.room_size - 2)
            x = (cell.x * self.room_size) + random.randint(
                1, self.room_size - width - 1
            )
            y = (cell.y * self.room_size) + random.randint(
                1, self.room_size - height - 1
            )
            floorTiles = []
            for i in range(width):
                for j in range(height):
                    floorTiles.append((x + i, y + j))
            cell.room = floorTiles
            rooms.append(floorTiles)

        # 7. For each connection between two cells:
        connections = {}
        for c in self.cells.values():
            for other in c.connectedTo:
                connections[tuple(sorted((c.id, other.id)))] = (c.room, other.room)
        for a, b in connections.values():
            # 7a. Create a random corridor between the rooms in each cell.
            start = random.choice(a)
            end = random.choice(b)

            corridor = []
            for tile in self._aStar(start, end):
                if tile not in a and tile not in b:
                    corridor.append(tile)
            rooms.append(corridor)

        # 8. Place staircases in the cell picked in step 2 and the lest cell visited in step 3b.
        stairsUp = random.choice(firstCell.room)
        stairsDown = random.choice(lastCell.room)

        # create tiles
        tiles = {}
        tilesX = self.rows * self.room_size
        tilesY = self.cols * self.room_size
        for x in range(tilesX):
            for y in range(tilesY):
                tiles[(x, y)] = " "
        for xy in itertools.chain.from_iterable(rooms):
            tiles[xy] = "."

        for xy, tile in tiles.items():
            if not tile == "." and "." in self.getNeighborTiles(xy, tiles):
                tiles[xy] = "#"
        tiles[stairsUp] = "<"
        tiles[stairsDown] = ">"

        # maze_string = ""
        # for y in range(tilesY):
        #     for x in range(tilesX):
        #         maze_string += tiles[(x, y)]
        #     sys.stdout.write("\n")

        return "".join(tiles.values())

    # 3. While the current cell has unconnected neighbor cells:
    def getNeighborCells(self, cell):
        for x, y in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            try:
                yield self.cells[(cell.x + x, cell.y + y)]
            except KeyError:
                continue

    def _aStar(self, start, goal):
        def heuristic(a, b):
            ax, ay = a
            bx, by = b
            return abs(ax - bx) + abs(ay - by)

        def reconstructPath(n):
            if n == start:
                return [n]
            return reconstructPath(cameFrom[n]) + [n]

        def neighbors(n):
            x, y = n
            return (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)

        closed = set()
        open = set()
        open.add(start)
        cameFrom = {}
        gScore = {start: 0}
        fScore = {start: heuristic(start, goal)}

        while open:
            current = None
            for i in open:
                if current is None or fScore[i] < fScore[current]:
                    current = i

            if current == goal:
                return reconstructPath(goal)

            open.remove(current)
            closed.add(current)

            for neighbor in neighbors(current):
                if neighbor in closed:
                    continue
                g = gScore[current] + 1

                if neighbor not in open or g < gScore[neighbor]:
                    cameFrom[neighbor] = current
                    gScore[neighbor] = g
                    fScore[neighbor] = gScore[neighbor] + heuristic(neighbor, goal)
                    if neighbor not in open:
                        open.add(neighbor)
        return ()

    # every tile adjacent to a floor is a wall
    def getNeighborTiles(self, xy, tiles):
        tx, ty = xy
        for x, y in (
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ):
            try:
                yield tiles[(tx + x, ty + y)]
            except KeyError:
                continue
