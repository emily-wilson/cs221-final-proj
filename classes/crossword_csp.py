from os import uname
from turtledemo.penrose import start
from typing import Callable
import random
from classes.puzzle import Puzzle
from classes.llm_domain_generator import LLMDomainGenerator
from classes.csp import CSP

class CrosswordCSP(CSP):
    def __init__(self, puzzle: Puzzle):
        super().__init__(puzzle)

        # CSP specific instance variables
        self.variables = set(self.puzzle.clues.keys())

        self.unary_constraints = {}
        self.binary_constraints = {}

        self.__setup_constraints__()

    def add_unary_constraint(self, variable: str, func: Callable):
        if variable not in self.unary_constraints:
            self.unary_constraints[variable] = set()
        self.unary_constraints[variable].add(func)

    def add_binary_constraint(self, v1: str, v2: str, func: Callable):
        if v1 not in self.binary_constraints:
            self.binary_constraints[v1] = set()
        if v2 not in self.binary_constraints:
            self.binary_constraints[v2] = set()
        self.binary_constraints[v1].add(func)
        self.binary_constraints[v2].add(func)

    def __setup_constraints__(self):
        grid = [[set() for _ in range(len(self.puzzle.grid[0]))] for _ in range(len(self.puzzle.grid))]
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
                self.add_binary_constraint(v1, v2, lambda c1, c2: c1[intersection[0]] == c2[intersection[1]])