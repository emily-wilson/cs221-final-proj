import utils
from learning.basic_backjumping import BasicBackjumping
from classes.csp import CSP

class DoubleBackjumping(BasicBackjumping):
    def __init__(self, csp: CSP):
        super().__init__(csp)
        self.assignment_weights = {}

    def __setup_constraints__(self):
        # print(f'ans lens: {self.csp.puzzle.ans_lens}')
        def lens_match(word, exp):
            return 1 if len(word) == exp else 0
        def get_len_matcher(k):
            return lambda word: lens_match(word, self.csp.puzzle.ans_lens[k])
        for k in self.csp.puzzle.clues.keys():
            self.csp.add_unary_constraint(k, get_len_matcher(k))

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
            if word2 is None:
                return 0.5
            if intersection[1] >= len(word1) or intersection[0] >= len(word2):
                # print(f'unequal word lens, w1: {word1}, w2: {word2}, intersection: {intersection}')
                return 0.1
            if word1[intersection[1]] is None or word2[intersection[0]] is None:
                # print(f'one word missing letter? {word1[intersection[1]]}, {word2[intersection[0]]}')
                return 0.1

            return 1.0 if word1[intersection[1]] == word2[intersection[0]] else 0

        def get_intersection_lambda(intersection):
            return lambda c1, c2: words_intersect(c1, c2, intersection)

        for v1 in self.csp.puzzle.clues.keys():
            for v2, intersection in self.csp.puzzle.dep_graph[v1]:
                self.csp.add_binary_constraint(v1, v2, get_intersection_lambda(intersection))

    def solve_iter(self):
        if self.domain is None:
            self.domain = self.domain_gen.generate_domains(self.csp.puzzle.clues)
            self.variable_ordering = super().__order_variables__(self.domain)
            self.assignment = {}

        if len(self.variable_ordering) > 0:
            priority, var = self.variable_ordering.pop()
            max_p = None
            for val in self.domain[var]:
                p = self.csp.compute_weight(var, val, self.assignment)
                if max_p is None or p > max_p[1]:
                    max_p = (val, p)
            # print(f'max_p = {max_p}')
            if max_p[1] < 0.5:
                self.potential_incorrect_answers.add(var)
            elif max_p[1] > 0:
                self.csp.puzzle.answer(var, max_p[0])
                self.assignment[var] = max_p[0]
            self.assignment_weights[var] = max_p[1]
            return None

        if self.i is None:
            # print(f'assignment: {self.assignment}, potential incorrect: {self.potential_incorrect_answers}')
            self.i = 1
            self.new_flagged_answers = set()
            self.potential_double_backjumps = set()

        if self.i < 4 and len(self.potential_incorrect_answers) > 0:
            var = self.potential_incorrect_answers.pop()
            max_p = None
            self.domain[var] |= self.domain_gen.generate_single_domain(var, self.domain[var],
                                                                 self.csp.puzzle.getPartialAnswer(var))
            new_domain = set()
            # print(f'partial: {self.csp.puzzle.getPartialAnswer(var)}')
            # print(f'new domain: {domain[var]}')
            for val in self.domain[var]:
                p = self.csp.compute_weight(var, val, self.assignment, flagged_answers = self.potential_incorrect_answers | self.new_flagged_answers)
                if max_p is None or p > max_p[1]:
                    max_p = (val, p)
                if p > 0:
                    new_domain.add(val)
            self.domain[var] = new_domain
            if max_p[1] > self.assignment_weights[var]:
                conflicting_vars = self.csp.getConflictingVars(var, max_p[0], self.assignment)
                # print(f'val: {max_p[0]}, conflicting vars: {conflicting_vars}')
                should_reassign = True
                for v in conflicting_vars:
                    if self.assignment_weights[v] > max_p[1]:
                        should_reassign = False
                if should_reassign:
                    self.assignment[var] = max_p[0]
                    self.assignment_weights[var] = max_p[1]
                    self.csp.puzzle.answer(var, max_p[0])
                    for key in conflicting_vars:
                        self.new_flagged_answers.add(key)
                else:
                    self.new_flagged_answers.add(var)
            else:
                self.new_flagged_answers.add(var)
            return None
        elif self.i < utils.MAX_ITER:
            self.i += 1
            # printprint(f'new flagged answers: ', self.new_flagged_answers)
            self.potential_incorrect_answers = self.new_flagged_answers | (self.csp.puzzle.clues.keys() - self.assignment.keys())
            self.potential_double_backjumps.clear()
            self.new_flagged_answers = set()
            return None

        return self.assignment
