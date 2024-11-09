from classes.baseline_domain_generator import BaselineDomainGenerator
from classes.crossword_csp import CrosswordCSP
import random

from classes.puzzle import Puzzle


class BaselineCSP(CrosswordCSP):
    def __init__(self, puzzle: Puzzle):
        super().__init__(puzzle)
        self.domain_gen = BaselineDomainGenerator(puzzle)

    def __get_variable(self, assignment, answer_domains, strategy = "mcv"):
        available_clues = self.puzzle.clues.keys() - assignment.keys()
        if strategy == "mcv":
            mcv = None
            for clue in available_clues:
                ans_passing_constraints = set()
                for ans in answer_domains:
                    for constraint in self.unary_constraints[clue]:
                        if constraint(ans):
                            ans_passing_constraints.add(ans)
                if len(ans_passing_constraints) != 0 and (mcv is None or len(ans_passing_constraints) < mcv[1]):
                    mcv = (clue, len(ans_passing_constraints))
            return mcv[0]
        return random.choice(available_clues)

    def solve(self):
        assignment = {}
        answer_domains = self.domain_gen.generate_domains(self.puzzle.clues)
        partial_answers = {}
        while len(assignment.keys()) < len(self.puzzle.clues.keys()):
            next_var = self.__get_variable(assignment, answer_domains)
            if len(answer_domains[next_var]) == 0:
                continue
            assignment[next_var] = answer_domains[next_var].pop()
            # print(next_var, answer_domains[next_var].pop())
            self.puzzle.answer(next_var, assignment[next_var])
        return assignment