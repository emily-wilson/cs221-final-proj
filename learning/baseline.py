from classes.baseline_domain_generator import BaselineDomainGenerator
from classes.puzzle import Puzzle
from classes.csp import CSP

class Baseline:
    def __init__(self, csp: CSP, temperature = 1.0):
        self.domain_gen = BaselineDomainGenerator(csp.puzzle, temperature)
        self.csp = csp


    def solve(self):
        return {k: v.pop() for k, v in self.domain_gen.generate_domains(self.csp.puzzle.clues, num_responses=1).items()}, 1
