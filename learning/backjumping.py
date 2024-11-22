from classes.baseline_domain_generator import BaselineDomainGenerator
from classes.priority_queue import PriorityQueue

class Backjumping:
    def __init__(self, csp):
        self.csp = csp
        self.domain_gen = BaselineDomainGenerator(csp.puzzle)
        self.__setup_constraints()

        self.potential_incorrect_answers = []

    def __setup_constraints(self):
        print(f'ans lens: {self.csp.puzzle.ans_lens}')
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

        dep_graph = {}
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                for m in grid[i][j]:
                    for n in grid[i][j]:
                        if m == n:
                            continue
                        if m not in dep_graph:
                            dep_graph[m] = set()
                        # if n not in dep_graph:
                        #     dep_graph[n] = set()
                        intersection = self.csp.puzzle.getIntersection(m, n)
                        dep_graph[m].add((n, intersection))
                        # dep_graph[n].add((m, intersection))
        print(f'dep graph: {dep_graph}')

        def words_intersect(word1, word2, intersection):
            # print(word1, word2, intersection)
            if intersection[1] >= len(word1) or intersection[0] >= len(word2):
                return 0.1
            if word1[intersection[1]] is None or word2[intersection[0]] is None:
                return 1

            return 1 if word1[intersection[1]] == word2[intersection[0]] else 0.1

        def get_intersection_lambda(intersection):
            return lambda c1, c2: words_intersect(c1, c2, intersection)

        for v1 in dep_graph:
            for v2, intersection in dep_graph[v1]:
                self.csp.add_binary_constraint(v1, v2, get_intersection_lambda(intersection))

    def __order_variables(self, domain):
        variable_ordering = PriorityQueue()
        for variable in domain.keys():
            variable_ordering.push(-len(domain[variable]), variable)
        return variable_ordering

    def solve(self):
        domain = self.domain_gen.generate_domains(self.csp.puzzle.clues)
        # print(f'domain: {domain}')
        variable_ordering = self.__order_variables(domain)
        assignment = {}

        while len(variable_ordering) > 0:
            priority, var = variable_ordering.pop()
            max_p = None
            for val in domain[var]:
                p = self.csp.compute_weight(var, val, assignment)
                if max_p is None or p > max_p[1]:
                    max_p = (val, p)
            # print(f'max_p = {max_p}')
            if max_p[1] < 1:
                self.potential_incorrect_answers.append(var)
            else:
                assignment[var] = max_p[0]
                self.csp.puzzle.answer(var, max_p[0])

        print(f'assignment: {assignment}, potential incorrect: {self.potential_incorrect_answers}')
        i = 1
        while i < 4 and len(self.potential_incorrect_answers) > 0:
            new_flagged_answers = []
            for var in self.potential_incorrect_answers:
                max_p = None
                domain[var] = self.domain_gen.generate_single_domain(var, domain[var], self.csp.puzzle.getPartialAnswer(var))
                print(f'partial: {self.csp.puzzle.getPartialAnswer(var)}')
                # print(f'new domain: {domain[var]}')
                for val in domain[var]:
                    p = self.csp.compute_weight(var, val, assignment)
                    if max_p is None or p > max_p[1]:
                        max_p = (val, p)
                print(f'max_p: {max_p}')
                if max_p[1] < 1/i:
                    new_flagged_answers.append(var)
                else:
                    assignment[var] = max_p[0]
                    self.csp.puzzle.answer(var, max_p[0])
            i += 1
            print(f'new flagged answers: ', new_flagged_answers)
            self.potential_incorrect_answers = new_flagged_answers
        return assignment
