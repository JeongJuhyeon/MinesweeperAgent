
class Node:
    def __init__(self, pos, is_mine):
        self.pos = pos
        self.is_mine = is_mine
        self.is_unrevealed = True
        self.adjacent_mines = 0

    def __str__(self):
        return f"Node @ {self.pos}, Mine: {self.is_mine}, Hidden: {self.is_unrevealed}, Adjacent: {self.adjacent_mines}"
