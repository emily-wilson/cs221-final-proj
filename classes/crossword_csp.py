from os import uname
from turtledemo.penrose import start
from typing import Callable
import random
from classes.puzzle import Puzzle
from classes.llm_domain_generator import LLMDomainGenerator

class CrosswordCSP:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.domain_gen = LLMDomainGenerator(puzzle)

        # CSP specific instance variables
        self.variables = set(self.puzzle.clues.keys())

        self.unary_constraints = {}
        self.binary_constraints = {}

        self.__setup_constraints__()

    def __add_unary_constraint(self, variable: str, func: Callable):
        if variable not in self.unary_constraints:
            self.unary_constraints[variable] = set()
        self.unary_constraints[variable].add(func)

    def __add_binary_constraint(self, v1: str, v2: str, func: Callable):
        if v1 not in self.binary_constraints:
            self.binary_constraints[v1] = set()
        if v2 not in self.binary_constraints:
            self.binary_constraints[v2] = set()
        self.binary_constraints[v1].add(func)
        self.binary_constraints[v2].add(func)

    def __setup_constraints__(self):
        # Add unary word length constraints first
        for k in self.puzzle.clues.keys():
            self.__add_unary_constraint(k, lambda x: len(x) == self.puzzle.ans_lens[k])

        grid = [[set() for _ in range(len(self.puzzle.grid[0]))] for _ in range(len(self.puzzle.grid))]
        for k in self.puzzle.clues.keys():
            start_ind = self.puzzle.clue_inds[k[:-1]]
            i, j = start_ind
            if k[-1] == 'd':
                while i < len(self.puzzle.grid) and self.puzzle.grid[i][j] != '-':
                    grid[i][j].add(k)
                    i += 1
            else:
                while j < len(self.puzzle.grid[0]) and self.puzzle.grid[i][j] != '-':
                    grid[i][j].add(k)
                    j += 1
        print(grid)
        dep_graph = {}
        for i in range(len(self.puzzle.grid)):
            for j in range(len(self.puzzle.grid[0])):
                for m in grid[i][j]:
                    for n in grid[i][j]:
                        if m == n:
                            continue
                        if m not in dep_graph:
                            dep_graph[m] = set()
                        if n not in dep_graph:
                            dep_graph[n] = set()
                        intersection = self.puzzle.getIntersection(m, n)
                        dep_graph[m].add((n, intersection))
                        dep_graph[n].add((m, intersection))

        for v1 in dep_graph:
            for v2, intersection in dep_graph[v1]:
                self.__add_binary_constraint(v1, v2, lambda c1, c2: c1[intersection[0]] == c2[intersection[1]])

    # Get the next variable to assign for the given assignment using the provided strategy
    def __get_variable(self, assignment, answer_domains, strategy = "mcv"):
        raise NotImplementedError("__get_variable is not implemented in CrosswordCSP")

    def solve(self):
        raise NotImplementedError("solve is not implemented in CrosswordCSP")

    def getAccuracy(self, assignment):
        correct_answers = 0
        for key in assignment.keys():
            if assignment[key] == self.puzzle.answers[key]:
                correct_answers += 1

        correct_square = 0
        for i in range(len(self.puzzle.grid)):
            for j in range(len(self.puzzle.grid[0])):
                if self.puzzle.grid[i][j] == self.puzzle.correct_grid[i][j]:
                    correct_square += 1
        return (correct_answers / len(self.puzzle.clues), correct_square / (len(self.puzzle.grid) * len(self.puzzle.grid[0])))