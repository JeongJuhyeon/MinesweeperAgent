from Minesweeper import Minesweeper
from AIBoard import AIBoard
import random
from time import sleep
import timeit

# random.seed(6)
random.seed()

socketio = None
WEB_CLIENT = False

minesweeper = None
aiBoard = None
GRIDSIZE = None
NO_MINES = None

statistics_list = []
statistics = {'gridsize': None, 'no_mines': None, 'time': None, 'evaluations': 0, 'games_won': 0, 'games_lost': 0,
              'type': ''}


def init(gridsize, no_mines):
    global minesweeper
    global aiBoard
    global GRIDSIZE
    global NO_MINES
    global statistics

    minesweeper = Minesweeper(gridsize, no_mines)
    aiBoard = AIBoard(gridsize)
    GRIDSIZE = gridsize
    NO_MINES = no_mines


def display_board():
    for r in minesweeper.nodes:
        for n in r:
            if n.is_unrevealed:
                s = "?"
            else:
                s = n.adjacent_mines
            print(f"{s}", end='')
        print()
        # print('-' * GRIDSIZE)
    print("\n\n@@@@@@@@@@@\n\n")


def update_views():
    if not WEB_CLIENT:
        return
    display_board()
    send_board(game_to_board_dict())


def game_to_board_dict():
    board_dict = {'board': []}
    for r in minesweeper.nodes:
        board_dict['board'].append([])
        for n in r:
            if n.is_unrevealed:
                an = aiBoard.get_ainode_from_msnode(n)
                if an.definitely_mine:
                    s = "🚩"
                elif an.cant_be_mine:
                    s = "✔️"
                else:
                    s = "?"
            else:
                if n.adjacent_mines == 0:
                    s = " "
                else:
                    s = str(n.adjacent_mines)
            board_dict['board'][-1].append(s)

    board_dict['found_mines'] = sum(an.definitely_mine for an in aiBoard.get_flat_nodes())

    return board_dict


# def initialize_algoboard():
#     for n in minesweeper.get_flat_nodes():
#         if not n.is_unrevealed:
#             aiBoard.nodes[n.pos[0]][n.pos[1]].cant_be_mine = True

def evaluate_surrounding_nodes_simple(x, y):
    statistics['evaluations'] += 1
    node = minesweeper.nodes[x][y]
    assert node.adjacent_mines > 0
    if node.is_unrevealed:
        return

    # All unrevealed adjacent nodes are mines
    if mark_mines(node) > 0:
        unrevealed_adj_nodes = list(filter(lambda n: n.is_unrevealed, minesweeper.get_adj_nodes(*node.pos)))
        for unrevealed_adj_node in unrevealed_adj_nodes:
            mark_safe(unrevealed_adj_node)
    # There are unrevealed non-mines around node
    mark_safe(node)


def mark_safe(node):
    unrevealed_adj_nodes = list(filter(lambda n: n.is_unrevealed, minesweeper.get_adj_nodes(*node.pos)))
    if len(unrevealed_adj_nodes) > node.adjacent_mines:
        adj_nodes_ai = [aiBoard.get_ainode_from_msnode(node) for node in unrevealed_adj_nodes]
        # We know which nodes are mines
        if sum(an.definitely_mine for an in adj_nodes_ai) == node.adjacent_mines:
            set_nodes_as_safe(unrevealed_adj_nodes)


def mark_mines(node):
    marked_mine = 0
    unrevealed_adj_nodes = list(filter(lambda n: n.is_unrevealed, minesweeper.get_adj_nodes(*node.pos)))
    if len(unrevealed_adj_nodes) == node.adjacent_mines:
        for n in unrevealed_adj_nodes:
            aiBoard.nodes[n.pos[0]][n.pos[1]].definitely_mine = True
            marked_mine += 1
    return marked_mine


def node_is_evaluatable(n):
    return (not n.is_unrevealed) and (n.adjacent_mines > 0)


def set_nodes_as_safe(unrevealed_adj_nodes):
    for n in unrevealed_adj_nodes:
        x, y = n.pos[0], n.pos[1]
        if not aiBoard.nodes[x][y].definitely_mine:
            aiBoard.nodes[x][y].cant_be_mine = True


def click_clickable_node():
    n = random.choice(aiBoard.get_safe_nodes())
    minesweeper.click(*n.pos)


def ai_solve_puzzle(bfs=True):
    queue = []
    queue.extend(list(filter(node_is_evaluatable, minesweeper.get_flat_nodes())))
    while queue:
        node_to_evaluate = queue.pop(0)
        evaluate_surrounding_nodes_simple(*node_to_evaluate.pos)
        safe_ms_nodes = list(map(minesweeper.get_msnode_from_ainode, aiBoard.get_safe_nodes()))
        unrevealed_safe_nodes = list(filter(lambda n: n.is_unrevealed, safe_ms_nodes))
        if unrevealed_safe_nodes:
            node_to_click = random.choice(unrevealed_safe_nodes)
            minesweeper.click(*node_to_click.pos)
            update_views()
            if game_is_won():
                print("GAME WON!!")
                statistics['games_won'] += 1
                if WEB_CLIENT:
                    sleep(2)
                return
            if WEB_CLIENT:
                sleep(0.2)
            for n in filter(node_is_evaluatable, minesweeper.get_flat_nodes()):
                if not n in queue:
                    if bfs:
                        queue.append(n)
                    else:
                        queue.insert(0, n)
    update_views()
    statistics['games_lost'] += 1
    if bfs:
        print("BFS: Could not find any more safe nodes :(")
    else:
        print("DFS: Could not find any more safe nodes :(")
    return


def game_is_won():
    return len(list(filter(lambda n: n.is_unrevealed, minesweeper.get_flat_nodes()))) == NO_MINES


def send_board(board_dict):
    if WEB_CLIENT:
        socketio.emit('board_update', board_dict)


def ai_start(socketioFromApp=None, web_client=False, bfs=True, gridsize=20, no_mines=40):
    init(gridsize, no_mines)
    statistics['type'] = 'bfs' if bfs else 'dfs'

    if web_client:
        global socketio
        global WEB_CLIENT
        socketio = socketioFromApp
        WEB_CLIENT = web_client
        print(minesweeper)
    else:
        random.seed()

    minesweeper.start_game()
    if WEB_CLIENT:
        socketio.emit('game_info', {'total_mines': NO_MINES, 'grid_size': minesweeper.gridsize})
    update_views()
    ai_solve_puzzle(bfs)


def gather_statistics():
    global statistics
    for gridsize in [10, 20, 30, 40]:
        for no_mines in [gridsize * gridsize // 20, gridsize * gridsize // 15, gridsize * gridsize // 10,
                         gridsize * gridsize // 5]:
            for bfs in [True, False]:
                statistics = {'gridsize': gridsize, 'no_mines': no_mines, 'time': None, 'evaluations': 0,
                              'games_won': 0, 'games_lost': 0,
                              'type': ''}
                statistics['time'] = timeit.timeit(f'ai_start(None, False, {bfs}, ' + str(gridsize) + ', ' + str(no_mines) + ')',
                                                   globals=globals(), number=100)
                statistics['win_rate'] = statistics['games_won'] / (statistics['games_won'] + statistics['games_lost'])
                statistics_list.append(statistics)
                print(len(statistics_list))

    write_statistics_to_csv()


def write_statistics_to_csv():
    import csv

    # csv_columns = ['Grid size (1 side)', '# mines', 'Time', 'Node Evaluations', 'Games Won', 'Games Lost', 'Algorithm']
    csv_columns = list(statistics.keys())
    csv_file = "Statistics.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in statistics_list:
                writer.writerow(data)
    except IOError:
        print("I/O error")


if __name__ == '__main__':
    gather_statistics()
