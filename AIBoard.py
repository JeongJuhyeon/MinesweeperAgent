from AINode import aiNode
import random

class AIBoard:
    def __init__(self, gridsize):
        self.nodes = [[aiNode((i, j)) for j in range(gridsize)] for i in range(gridsize)]

    def get_safe_nodes(self):
        flat = [n for r in self.nodes for n in r]
        return [n for n in flat if n.cant_be_mine]

    def get_flat_nodes(self):
        return [n for r in self.nodes for n in r]

    def get_ainode_from_msnode(self, n):
        return self.nodes[n.pos[0]][n.pos[1]]