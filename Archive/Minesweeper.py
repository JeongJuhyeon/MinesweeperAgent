from Node import Node
import random

class Minesweeper:
    def __init__(self, gridsize, no_mines):
        self.no_mines = no_mines
        self.gridsize = gridsize

        self.nodes = [[Node((i, j), False) for j in range(gridsize)] for i in range(gridsize)]
        mine_indices = random.sample([(a, b) for a in range(gridsize) for b in range(gridsize)], k=no_mines)
        for mine_node_loc in mine_indices:
            x, y = mine_node_loc[0], mine_node_loc[1]
            self.nodes[x][y].is_mine = True
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if not (0 <= x + i < gridsize and 0 <= y + j < gridsize):
                        continue
                    self.nodes[x + i][y + j].adjacent_mines += 1

        assert sum(n.is_mine for n in self.get_flat_nodes()) == no_mines

    def __str__(self):
        s = ""
        for r in self.nodes:
            for n in r:
                s += str(n) + '\n'
        return s

    def get_flat_nodes(self):
        return [n for r in self.nodes for n in r]

    def get_adj_nodes(self, x, y):
        anodes = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (0 <= x + i < self.gridsize and 0 <= y + j < self.gridsize):
                    continue
                anodes.append(self.nodes[x + i][y + j])
        return anodes

    def click(self, x, y):
        if self.nodes[x][y].is_mine:
            print(f"GAME OVER: Clicked on" + str(self.nodes[x][y]))
            exit()

        self.nodes[x][y].is_unrevealed = False

        if self.nodes[x][y].adjacent_mines == 0:
            self.open_empty_space_recursive(x, y)

        # for i in range(-1, 2):
        #     for j in range(-1, 2):
        #         if not (0 <= x + i < gridsize and 0 <= y + j < gridsize):
        #             continue
        #         self.update_node(x + i, y + j)

    def open_empty_space_recursive(self, x, y):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (0 <= x + i < self.gridsize and 0 <= y + j < self.gridsize):
                    continue
                if self.nodes[x + i][y + j].adjacent_mines == 0 and self.nodes[x + i][y + j].is_unrevealed:
                    self.nodes[x + i][y + j].is_unrevealed = False
                    self.open_empty_space_recursive(x + i, j + y)
                else:
                    self.nodes[x + i][y + j].is_unrevealed = False

    def start_game(self):
        starting_node = random.choice([n for n in self.get_flat_nodes() if n.adjacent_mines == 0])
        self.click(starting_node.pos[0], starting_node.pos[1])

    def get_msnode_from_ainode(self, n):
        return self.nodes[n.pos[0]][n.pos[1]]