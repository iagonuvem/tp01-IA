# coding:utf-8
import importlib
import random
import setup
import qlearn
import config as cfg
import queue

importlib.reload(setup)
importlib.reload(qlearn)


def pick_random_location():
    while 1:
        x = random.randrange(world.width)
        y = random.randrange(world.height)
        cell = world.get_cell(x, y)
        if not (cell.wall or len(cell.agents) > 0):
            return cell

class Coordinate(setup.World):
    def __init__(self):
        self.x = None
        self.y = None

class Cat(setup.Agent):
    def __init__(self, filename):
        self.cell = None
        self.catWin = 0
        self.color = cfg.cat_color
        f = open(filename)
        lines = f.readlines()
        lines = [x.rstrip() for x in lines]
        self.fh = len(lines)
        self.fw = max([len(x) for x in lines])
        self.grid_list = [[1 for x in range(self.fw)] for y in range(self.fh)]
        self.move = [(0, -1), (1, -1), (
                1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]

        for y in range(self.fh):
            line = lines[y]
            for x in range(min(self.fw, len(line))):
                t = 1 if (line[x] == 'X') else 0
                self.grid_list[y][x] = t

        # print("cat init success......")

    # using BFS algorithm to move quickly to target.
    def bfs_move(self, target):
        if self.cell == target:
            return

        for n in self.cell.neighbors:
            if n == target:
                self.cell = target  # if next move can go towards target
                return

        best_move = None
        q = queue.Queue()
        start = (self.cell.y, self.cell.x)
        end = (target.y, target.x)
        q.put(start)
        step = 1
        V = {}
        preV = {}
        V[(start[0], start[1])] = 1

        print("begin BFS......")
        while not q.empty():
            grid = q.get()

            for i in range(8):
                ny, nx = grid[0] + self.move[i][0], grid[1] + self.move[i][1]
                if nx < 0 or ny < 0 or nx > (self.fw-1) or ny > (self.fh-1):
                    continue
                if self.get_value(V, (ny, nx)) or self.grid_list[ny][nx] == 1:  # has visit or is wall.
                    continue

                preV[(ny, nx)] = self.get_value(V, (grid[0], grid[1]))
                if ny == end[0] and nx == end[1]:
                    V[(ny, nx)] = step + 1
                    seq = []
                    last = V[(ny, nx)]
                    while last > 1:
                        k = [key for key in V if V[key] == last]
                        seq.append(k[0])
                        assert len(k) == 1
                        last = preV[(k[0][0], k[0][1])]
                    seq.reverse()
                    print(seq)

                    best_move = world.grid[seq[0][0]][seq[0][1]]

                q.put((ny, nx))
                step += 1
                V[(ny, nx)] = step

        if best_move is not None:
            self.cell = best_move

        else:
            dir = random.randrange(cfg.directions)
            self.go_direction(dir)
            print("!!!!!!!!!!!!!!!!!!")

    def get_value(self, mdict, key):
        try:
            return mdict[key]
        except KeyError:
            return 0

    def update(self):
        print("cat update begin..")
        if self.cell != mouse.cell:
            self.bfs_move(mouse.cell)
            print("cat move..")


class Cheese(setup.Agent):
    def __init__(self):
        self.color = cfg.cheese_color

    def update(self):
        print("cheese update...")
        pass


class Mouse(setup.Agent):
    def __init__(self):
        self.ai = None
        self.ai = qlearn.QLearn(actions=range(cfg.directions), alpha=0.1, gamma=0.9, epsilon=0.1)
        self.catWin = 0
        self.mouseWin = 0
        self.lastState = None
        self.lastAction = None
        self.color = cfg.mouse_color

        print("mouse init...")

    def update(self):
        print("mouse update begin...")
        state = self.calculate_state()
        reward = cfg.MOVE_REWARD

        if self.cell == cat.cell:
            print("eaten by cat...")
            self.catWin += 1
            reward = cfg.EATEN_BY_CAT
            if self.lastState is not None:
                self.ai.learn(self.lastState, self.lastAction, state, reward)
                print("mouse learn...")
            self.lastState = None
            self.cell = pick_random_location()
            print("mouse random generate..")
            return

        # if self.cell == cheese.cell:
        #     self.mouseWin += 1
        #     reward = 50
        #     cheese.cell = pick_random_location()

        if self.lastState is not None:
            self.ai.learn(self.lastState, self.lastAction, state, reward)

        # choose a new action and execute it
        action = self.ai.choose_action(state)
        self.lastState = state
        self.lastAction = action
        self.go_direction(action)

    def calculate_state(self):
        def cell_value(cell):
            if cat.cell is not None and (cell.x == cat.cell.x and cell.y == cat.cell.y):
                return 3
            # elif cheese.cell is not None and (cell.x == cheese.cell.x and cell.y == cheese.cell.y):
            #     return 2
            else:
                return 1 if cell.wall else 0

        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        return tuple([cell_value(world.get_relative_cell(self.cell.x + dir[0], self.cell.y + dir[1])) for dir in dirs])

if __name__ == '__main__':
    mouse = Mouse()
    mouse2 = Mouse()
    mouse3 = Mouse()
    mouse4 = Mouse()
    mouse5 = Mouse()
    mouse6 = Mouse()

    cat = Cat(filename='resources/world.txt')
    cheese = Cheese()
    world = setup.World(filename='resources/world.txt')

    world.add_agent(mouse, cell=world.get_cell(2, 2))
    world.add_agent(mouse2, cell=world.get_cell(3, 2))
    world.add_agent(mouse3, cell=world.get_cell(4, 2))
    world.add_agent(mouse4, cell=world.get_cell(8, 2))
    world.add_agent(mouse5, cell=world.get_cell(9, 2))
    world.add_agent(mouse6, cell=world.get_cell(10, 2))

    # world.add_agent(cheese, cell=pick_random_location())
    world.add_agent(cat, cell=world.get_cell(5, 10))
    world.display.activate()
    world.display.speed = cfg.speed

    while 1:
        if(world.catTurn):
            row = input('Digite a Linha para se mover(x)..')
            col = input('Digite a Coluna para se mover(y)..')
            # cat.move()
            newPos = Coordinate()
            newPos.x = row
            newPos.y = col

            cat.bfs_move(newPos)

        world.update(mouse.mouseWin, mouse.catWin)
