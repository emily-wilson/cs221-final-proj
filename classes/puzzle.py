import json
import pygame
import util.utils as utils
import pygame.gfxdraw

class Puzzle:
    def __init__(self, filename):
        with open(filename, 'r') as file:
            object = json.load(file)

        self.clues = object["clues"]
        self.answers = object["answers"]
        self.numbers = object["numbers"]

        self.grid = [['-' if x == '-' else '' for x in self.numbers[i]] \
                       for i in range(len(self.numbers))]
        self.correct_grid = [['-' if x == '-' else '' for x in self.numbers[i]] \
                       for i in range(len(self.numbers))]
        self.ans_lens = {}

        self.__process_numbers()

    # Builds map of clue keys to starting position grid indices
    def __build_clue_inds(self):
        self.clue_inds = {}
        for i, row in enumerate(self.numbers):
            for j, item in enumerate(row):
                if len(item) > 0 and item != '-':
                    self.clue_inds[item] = (i, j)

    # Builds list of square rects for rendering the puzzle
    def __build_renderable_points(self):
        self.renderable_points = {}
        for i, row in enumerate(self.numbers):
            for j, item in enumerate(row):
                self.renderable_points[(i, j)] = [
                    (j * utils.SQUARE_SIZE, i * utils.SQUARE_SIZE),
                    ((j + 1) * utils.SQUARE_SIZE, i * utils.SQUARE_SIZE),
                    ((j + 1) * utils.SQUARE_SIZE, (i + 1) * utils.SQUARE_SIZE),
                    (j * utils.SQUARE_SIZE, (i + 1) * utils.SQUARE_SIZE)
                ]

    # Builds solution grid to compare answer to when rendering and computing accuracy
    def __build_solution_grid(self):
        for k in self.clues.keys():
            start_ind = self.clue_inds[k[:-1]]
            correct_answer = self.answers[k]
            i, j = start_ind
            if k[-1] == 'd':
                while i < len(self.grid) and self.grid[i][j] != '-':
                    self.correct_grid[i][j] = correct_answer[i - start_ind[0]]
                    i += 1
            else:
                while j < len(self.grid[0]) and self.grid[i][j] != '-':
                    self.correct_grid[i][j] = correct_answer[j - start_ind[1]]
                    j += 1

    # Builds map of clue key to answer length
    def __build_ans_lens(self):
        for k in self.clues.keys():
            start_ind = self.clue_inds[k[:-1]]
            i, j = start_ind
            if k[-1] == 'd':
                while i < len(self.grid) and self.grid[i][j] != '-':
                    i += 1
                self.ans_lens[k] = (i - start_ind[0])
            else:
                while j < len(self.grid[0]) and self.grid[i][j] != '-':
                    j += 1
                self.ans_lens[k] = (j - start_ind[1])
        # print(f'ans_lens contains all answers: {self.ans_lens.keys() == self.clues.keys()}')

    # Builds the dependency graph of all intersecting clues
    def __build_dep_graph(self):
        grid = [[set() for _ in range(len(self.grid[0]))] for _ in range(len(self.grid))]
        for k in self.clues.keys():
            start_ind = self.clue_inds[k[:-1]]
            i, j = start_ind
            if k[-1] == 'd':
                while i < len(self.grid) and self.grid[i][j] != '-':
                    grid[i][j].add(k)
                    i += 1
            else:
                while j < len(self.grid[0]) and self.grid[i][j] != '-':
                    grid[i][j].add(k)
                    j += 1

        self.dep_graph = {}
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                for m in grid[i][j]:
                    for n in grid[i][j]:
                        if m == n:
                            continue
                        if m not in self.dep_graph:
                            self.dep_graph[m] = set()
                        intersection = self.getIntersection(m, n)
                        self.dep_graph[m].add((n, intersection))
        # print(f'dep graph: {self.dep_graph}')

    # Preprocess the puzzle grid to efficiently make queries
    def __process_numbers(self):
        self.__build_clue_inds()
        self.__build_renderable_points()
        self.__build_solution_grid()
        self.__build_ans_lens()
        self.__build_dep_graph()

    ## Fill in the answer into the result puzzle
    def answer(self, clueNum: str, answer: str, force_clear=False):
        r, c = self.clue_inds[clueNum[:-1]]

        if clueNum[-1] == "a":
            for i in range(len(answer)):
                if c + i >= len(self.numbers[r]):
                    return
                    # print('Answer length exceeds puzzle size!')
                elif self.grid[r][c + i] == '-':
                    return
                    # print('Answer does not fit in puzzle!')
                elif force_clear or len(self.grid[r][c+i]) == 0:
                    self.grid[r][c + i] = answer[i]
        elif clueNum[-1] == "d":
            for i in range(len(answer)):
                if r + i >= len(self.numbers):
                    return
                    # print('Answer length exceeds puzzle size!')
                elif self.grid[r + i][c] == '-':
                    return
                    # print('Answer does not fit in puzzle!')
                elif force_clear or len(self.grid[r + i][c]) == 0:
                    self.grid[r + i][c] = answer[i]

    def clear_answer(self, clueNum: str):
        r, c = self.clue_inds[clueNum[:-1]]

        if clueNum[-1] == "a":
            for i in range(self.ans_lens[clueNum]):
                self.grid[r][c + i] = ''
        elif clueNum[-1] == "d":
            for i in range(self.ans_lens[clueNum]):
                self.grid[r + i][c] = ''

    def clear_grid(self):
        for k in self.clues.keys():
            self.clear_answer(k)

    def render(self, surface: pygame.Surface, wordFont: pygame.font.Font, numFont: pygame.font.Font):
        surface.fill('white')

        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j] == '-':
                    pygame.gfxdraw.filled_polygon(surface, self.renderable_points[(i, j)], (0, 0, 0))
                else:
                    points = self.renderable_points[(i, j)]
                    pygame.gfxdraw.polygon(surface, points, (0, 0, 0))
                    if len(self.grid[i][j]) != 0:
                        color = (0, 0, 0) if self.correct_grid[i][j] == self.grid[i][j] else (255, 0,0)
                        w_s = wordFont.render(self.grid[i][j], True, color)
                        w_rect = w_s.get_rect()
                        w_rect.center = (points[0][0] + (0.5 * utils.SQUARE_SIZE), points[0][1] + (0.5 * utils.SQUARE_SIZE))
                        surface.blit(w_s, w_rect)
                    if len(self.numbers[i][j]) != 0:
                        n_s = numFont.render(self.numbers[i][j], True, (0, 0, 0))
                        n_rect = n_s.get_rect()
                        n_rect.center = (points[0][0] + (0.2 * utils.SQUARE_SIZE), points[0][1] + (0.2 * utils.SQUARE_SIZE))
                        surface.blit(n_s, n_rect)


    def getScreenSize(self):
        return (len(self.grid[0]) * utils.SQUARE_SIZE, len(self.grid) * utils.SQUARE_SIZE)

    # Gets point where 2 clues intersect in form (clue1_ind, clue2_ind)
    def getIntersection(self, clue1: str, clue2: str) -> tuple:
        c1_start = self.clue_inds[clue1[:-1]]
        c2_start = self.clue_inds[clue2[:-1]]
        if clue1[-1] == 'd':
            return (abs(c1_start[1] - c2_start[1]), abs(c1_start[0] - c2_start[0]))
        else:
            return (abs(c1_start[0] - c2_start[0]), abs(c1_start[1] - c2_start[1]))

    def getPartialAnswer(self, clue):
        partial = ""
        start_ind = self.clue_inds[clue[:-1]]
        i, j = start_ind
        for x in range(self.ans_lens[clue]):
            c = ' '
            if clue[-1] == 'd':
                c = self.grid[i+x][j]
            else:
                c= self.grid[i][j+x]
            if len(c) > 0:
                partial += c
            else:
                partial += ' '
        return partial

    # Given clue number `key`, return all clue keys that intersect with this clue
    def getIntersectingClues(self, key):
        return [k for k, _ in self.dep_graph[key]]