import json
import pygame
import utils
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
        self.ans_lens = {}

        self.__process_numbers()


    ## Make a map of start indices of all clue numbers
    ##
    ## self.clue_inds = Dict[string, tuple]
    def __process_numbers(self):
        self.clue_inds = {}
        self.renderable_points = {}
        print(self.numbers)
        for i, row in enumerate(self.numbers):
            for j, item in enumerate(row):
                if len(item) > 0 and item != '-':
                    self.clue_inds[item] = (i, j)
                self.renderable_points[(i, j)] = [
                    (j*utils.SQUARE_SIZE, i*utils.SQUARE_SIZE),
                    ((j+1)*utils.SQUARE_SIZE, i*utils.SQUARE_SIZE),
                    ((j + 1) * utils.SQUARE_SIZE, (i + 1) * utils.SQUARE_SIZE),
                    (j*utils.SQUARE_SIZE, (i + 1)*utils.SQUARE_SIZE)
                ]

        for k in self.clues.keys():
            start_ind = self.clue_inds[k[:-1]]
            i, j = start_ind
            if k[-1] == 'd':
                while i < len(self.grid) and self.grid[i][j] != '-':
                    i += 1
                self.ans_lens[k] = i - start_ind[0]
            else:
                while j < len(self.grid[0]) and self.grid[i][j] != '-':
                    j += 1
                self.ans_lens[k] = j - start_ind[1]

    ## Fill in the answer into the result puzzle
    def answer(self, clueNum: str, answer: str):
        r, c = self.clue_inds[clueNum[:-1]]

        if clueNum[-1] == "a":
            for i in range(len(answer)):
                if c + i > len(self.numbers[r]):
                    print('Answer length exceeds puzzle size!')
                elif self.grid[r][c + i] == '-':
                    print('Answer does not fit in puzzle!')
                else:
                    self.grid[r][c + i] = answer[i]
        elif clueNum[-1] == "d":
            for i in range(len(answer)):
                if r + i > len(self.numbers):
                    print('Answer length exceeds puzzle size!')
                elif self.grid[r + i][c] == '-':
                    print('Answer does not fit in puzzle!')
                else:
                    self.grid[r + i][c] = answer[i]

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
                        w_s = wordFont.render(self.grid[i][j], True, (255, 0, 0))
                        w_rect = w_s.get_rect()
                        w_rect.center = (points[0][0] + (0.5*utils.SQUARE_SIZE), points[0][1] + (0.5*utils.SQUARE_SIZE))
                        surface.blit(w_s, w_rect)
                    if len(self.numbers[i][j]) != 0:
                        n_s = numFont.render(self.numbers[i][j], True, (0, 0, 0))
                        n_rect = n_s.get_rect()
                        n_rect.center = (points[0][0] + (0.2*utils.SQUARE_SIZE), points[0][1] + (0.2*utils.SQUARE_SIZE))
                        surface.blit(n_s, n_rect)


    def getScreenSize(self):
        return (len(self.grid[0])*utils.SQUARE_SIZE, len(self.grid) * utils.SQUARE_SIZE)

    # Gets point where 2 clues intersect in form (clue1_ind, clue2_ind)
    def getIntersection(self, clue1: str, clue2: str) -> tuple:
        c1_start = self.clue_inds[clue1[:-1]]
        c2_start = self.clue_inds[clue2[:-1]]
        if clue1[-1] == 'd':
            return (abs(c1_start[1] - c2_start[0]), abs(c1_start[0] - c2_start[0]))
        else:
            return (abs(c1_start[0] - c2_start[0]), abs(c1_start[1] - c2_start[1]))