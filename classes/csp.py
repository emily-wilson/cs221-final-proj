from os import uname
from turtledemo.penrose import start
from typing import Callable
import random
from classes.puzzle import Puzzle

class CSP:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

        # CSP specific instance variables
        self.variables = set(self.puzzle.clues.keys())

        self.unary_constraints = {}
        self.binary_constraints = {}

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

    # Get the next variable to assign for the given assignment using the provided strategy
    def get_variable(self, assignment, domains, strategy="mcv"):
        available_clues = self.puzzle.clues.keys() - assignment.keys()
        if strategy == "mcv":
            mcv = None
            for clue in available_clues:
                if len(domains[clue]) != 0 and (mcv is None or len(domains[clue]) < mcv[1]):
                    mcv = (clue, len(domains[clue]))
            return mcv[0]
        # print(f'available clues: {available_clues}')
        return random.choice(list(available_clues))

    def compute_weight(self, var, val, assignment):
        prod = 1
        if var in self.unary_constraints:
            for f in self.unary_constraints[var]:
                prod *= f(val)
        if var in self.binary_constraints:
            binary_constraints = self.binary_constraints[var]
            print(f'num binary constraints: {len(binary_constraints)}')
        return prod

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