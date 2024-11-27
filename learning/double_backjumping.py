import utils
from learning.basic_backjumping import BasicBackjumping
from classes.csp import CSP

class DoubleBackjumping(BasicBackjumping):
    def __init__(self, csp: CSP):
        super().__init__(csp)

    def __setup_constraints__(self):
        print(f'setting up double backjumping constraints')
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
            print(word1, word2, intersection)
            if intersection[1] >= len(word1):
                print(f'val: {0}')
                return 0
            if intersection[0] >= len(word2):
                return 1
            if word1[intersection[1]] is None or word2[intersection[0]] is None:
                print(f'val: {1}')
                return 1

            print(f'val: {1 if word1[intersection[1]] == word2[intersection[0]] else 0}')
            return 1.4 if word1[intersection[1]] == word2[intersection[0]] else 0

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
                p = self.csp.compute_weight(var, val, self.assignment, flagged_answers=self.potential_incorrect_answers)
                if max_p is None or p > max_p[1]:
                    max_p = (val, p)
            # print(f'max_p = {max_p}')
            if max_p[1] < 1:
                self.potential_incorrect_answers.add(var)
            self.assignment[var] = max_p[0]
            self.csp.puzzle.answer(var, max_p[0], force_clear=max_p[1]==1)
            return None

        if self.i is None:
            print(f'assignment: {self.assignment}, potential incorrect: {self.potential_incorrect_answers}')
            self.i = 1
            self.new_flagged_answers = set()
            self.potential_double_backjumps = set()

        if self.i < 4 and len(self.potential_incorrect_answers) > 0:
            var = self.potential_incorrect_answers.pop()
            max_p = None
            self.domain[var] |= self.domain_gen.generate_single_domain(var, self.domain[var])
            print(f'new domain: {self.domain[var]}')
            # print(f'partial: {self.csp.puzzle.getPartialAnswer(var)}')
            # print(f'new domain: {domain[var]}')
            for val in self.domain[var]:
                p = self.csp.compute_weight(var, val, self.assignment, flagged_answers=self.potential_incorrect_answers | self.new_flagged_answers)
                if max_p is None or p > max_p[1]:
                    max_p = (val, p)
            if max_p[1] == 1:
                # Found an answer that fits perfectly
                self.assignment[var] = max_p[0]
                self.csp.puzzle.answer(var, max_p[0], force_clear=True)
            elif var in self.assignment and max_p[1] > self.csp.compute_weight(var, self.assignment[var], self.assignment, flagged_answers=self.potential_incorrect_answers | self.new_flagged_answers):
                # Found an answer that might fit
                self.assignment[var] = max_p[0]
                self.csp.puzzle.answer(var, max_p[0])
                self.new_flagged_answers.add(var)
            else:
                print(f'max_p: {max_p}')
                self.new_flagged_answers.add(var)
                conflicting_vars = self.csp.getConflictingVars(var, max_p[0], self.assignment)
                for key in conflicting_vars:
                    var_weight = self.csp.compute_weight(key, self.assignment[key], self.assignment, flagged_answers=self.potential_incorrect_answers | self.new_flagged_answers)
                    if var_weight <= max_p[1]:
                        print(f'key: {key}, val: {self.assignment[key]}, var weight: {var_weight}')
                        # del self.assignment[key]
                        # self.csp.puzzle.clear_answer(key)
                        self.new_flagged_answers.add(key)
                        # add answer to assignment since it is more confident than a replacement
                        self.assignment[var] = max_p[0]
                        self.csp.puzzle.answer(var, max_p[0], force_clear=True)
            return None
        elif self.i < utils.MAX_ITER:
            self.i += 1
            print(f'new flagged answers: ', self.new_flagged_answers)
            self.potential_incorrect_answers.clear()
            self.potential_incorrect_answers.union(self.new_flagged_answers)

            self.potential_double_backjumps.clear()
            self.new_flagged_answers = set()
            return None

        # for k, v in self.assignment.items():
        #     print(f'k: {k}, v: {v}')
        #     self.csp.puzzle.answer(k, v, force_clear=True)
        return self.assignment
