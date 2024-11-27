import math
import utils
import random
from classes.baseline_domain_generator import BaselineDomainGenerator
from classes.priority_queue import PriorityQueue


class WalkSat:
    def __init__(self, csp):
        self.csp = csp
        self.domain_gen = BaselineDomainGenerator(csp.puzzle)
        self.__setup_constraints__()

        self.assignment = {}
        self.domain = None
        self.i = 0
        self.j = 0
        self.hard_unsat = set()
        self.soft_unsat = set()
        self.total_unsat_weight = 0

    def __setup_constraints__(self):
        def lens_match(word, exp):
            return 0 if len(word) == exp else utils.HARD_SAT_WEIGHT
        def get_len_matcher(k):
            return lambda word: lens_match(word, self.csp.puzzle.ans_lens[k])
        # for k in self.csp.puzzle.clues.keys():
        #     self.csp.add_unary_constraint(k, get_len_matcher(k))

        grid = [[set() for _ in range(len(self.csp.puzzle.grid[0]))] for _ in range(len(self.csp.puzzle.grid))]
        for k in self.csp.puzzle.clues.keys():
            start_ind = self.csp.puzzle.clue_inds[k[:-1]]
            i, j = start_ind
            if k[-1] == 'd':
                while i < len(self.csp.puzzle.grid) and self.csp.puzzle.grid[i][j] != '-':
                    grid[i][j].add(k)
                    i += 1
            else:
                while j < len(self.csp.puzzle.grid[0]) and self.csp.puzzle.grid[i][j] != '-':
                    grid[i][j].add(k)
                    j += 1

        # For binary constraint, word 2 is taken from the assignment and word1 is being tested.
        def words_intersect(word1, word2, intersection):
            # print(word1, word2, intersection)
            if intersection[1] >= len(word1):
                return 10
            if intersection[0] >= len(word2):
                return 1
            if word1[intersection[1]] is None or word2[intersection[0]] is None:
                return 1

            return 0 if word1[intersection[1]] == word2[intersection[0]] else 1

        def get_intersection_lambda(intersection):
            return lambda c1, c2: words_intersect(c1, c2, intersection)

        for v1 in self.csp.puzzle.clues.keys():
            for v2, intersection in self.csp.puzzle.dep_graph[v1]:
                self.csp.add_binary_constraint(v1, v2, get_intersection_lambda(intersection))

    # Assigns the max probability item to the variable and returns probability
    def __assign_max_prob__(self, var, domain) -> float:
        max_p = None
        for item in domain:
            p = self.csp.compute_weight(var, item, self.assignment)
            if max_p is None or p < max_p[0]:
                max_p = (p, item)
        self.csp.puzzle.answer(var, max_p[1], force_clear=True)
        self.assignment[var] = max_p[1]
        return max_p[0]

    def __get_total_unsat_weight__(self):
        return sum([p for var, p in self.hard_unsat] +
            [p for var, p in self.soft_unsat])

    def solve(self):
        # initial assignment
        self.domain = self.domain_gen.generate_domains(self.csp.puzzle.clues.keys(), num_responses=4)
        for var, domain in self.domain.items():
            p = self.__assign_max_prob__(var, domain)
            if p >= utils.HARD_SAT_WEIGHT:
                self.hard_unsat.add((var, p))
            elif p > 0:
                self.soft_unsat.add((var, p))
        print(self.assignment)
        print(f'hard unsat: {self.hard_unsat}')
        print(f'soft unsat: {self.soft_unsat}')

        self.total_unsat_weight = self.__get_total_unsat_weight__()

        for i in range(utils.MAX_ITER):
            for j in range(10):
                c = None
                print(f'hard unsat: {self.hard_unsat}, soft unsat: {self.soft_unsat}')
                if len(self.hard_unsat) > 0 and random.random() > utils.ETA:
                    c, p = random.choice(list(self.hard_unsat))
                    print(c)
                    self.hard_unsat.remove((c, p))
                elif len(self.soft_unsat) > 0:
                    c, p = random.choice(list(self.soft_unsat))
                    print(c)
                    self.soft_unsat.remove((c, p))
                print(c)
                if c is None:
                    continue
                prev_assignment = self.assignment[c]
                self.domain[c] |= self.domain_gen.generate_single_domain(c, self.domain[c], self.csp.puzzle.getPartialAnswer(c))
                p = self.__assign_max_prob__(c, self.domain)
                hu = set()
                su = set()
                for var, item in self.assignment.items():
                    p_prime = self.csp.compute_weight(var, item, self.assignment)
                    if p >= utils.HARD_SAT_WEIGHT:
                        hu.add((var, p_prime))
                    elif p > 0:
                        su.add((var, p_prime))
                new_weight = sum([w for v, w in hu] + [w for v, w in su])
                if prev_assignment is not None and new_weight > self.total_unsat_weight:
                    self.csp.puzzle.answer(c, prev_assignment, force_clear=True)
                    self.assignment[c] = prev_assignment
                else:
                    self.total_unsat_weight = new_weight
                    self.hard_unsat |= hu
                    self.soft_unsat |= su


    def solve_iter(self):
        if self.i == 0:
            self.domain = self.domain_gen.generate_domains(self.csp.puzzle.clues.keys(), num_responses=4)
            for var, domain in self.domain.items():
                p = self.__assign_max_prob__(var, domain)
                if p >= utils.HARD_SAT_WEIGHT:
                    self.hard_unsat.add((var, p))
                elif p > 0:
                    self.soft_unsat.add((var, p))
            print(self.assignment)
            # print(f'hard unsat: {self.hard_unsat}')
            # print(f'soft unsat: {self.soft_unsat}')

            self.total_unsat_weight = self.__get_total_unsat_weight__()
            self.i += 1
            return None
        if self.i < utils.MAX_ITER:
            if self.j < len(self.csp.puzzle.clues.keys()):
                c = None
                # print(f'hard unsat: {self.hard_unsat}, soft unsat: {self.soft_unsat}')
                if len(self.hard_unsat) > 0 and random.random() > utils.ETA:
                    c, p = random.choice(list(self.hard_unsat))
                    self.hard_unsat.remove((c, p))
                elif len(self.soft_unsat) > 0:
                    c, p = random.choice(list(self.soft_unsat))
                    self.soft_unsat.remove((c, p))
                print(c)
                if c is None:
                    return self.assignment
                prev_assignment = self.assignment[c]
                self.domain[c] |= self.domain_gen.generate_single_domain(c, self.domain[c], self.csp.puzzle.getPartialAnswer(c))
                print(f'prev assignment: {prev_assignment}')
                p = self.__assign_max_prob__(c, self.domain[c])
                print(f'new assignment: {self.assignment[c]}')
                hu = set()
                su = set()
                for var, item in self.assignment.items():
                    p_prime = self.csp.compute_weight(var, item, self.assignment)
                    if p_prime >= utils.HARD_SAT_WEIGHT:
                        hu.add((var, p_prime))
                    elif p_prime > 0:
                        su.add((var, p_prime))
                new_weight = sum([w for v, w in hu] + [w for v, w in su])
                print(f'old weight: {self.total_unsat_weight}, new weight: {new_weight}')
                if prev_assignment is not None and new_weight > self.total_unsat_weight:
                    self.csp.puzzle.answer(c, prev_assignment, force_clear=True)
                    self.assignment[c] = prev_assignment
                    if p >= utils.HARD_SAT_WEIGHT:
                        self.hard_unsat.add((c, p))
                    elif p > 0:
                        self.soft_unsat.add((c, p))
                else:
                    print(f'flipping {c} to {self.assignment[c]}')
                    self.hard_unsat |= hu
                    self.soft_unsat |= su
                    self.total_unsat_weight = new_weight
                self.j += 1
                return None
            else:
                self.i += 1
                return None
        return self.assignment
