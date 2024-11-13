import utils
from classes.baseline_domain_generator import BaselineDomainGenerator
import random

from classes.priority_queue import PriorityQueue


class AStartSearch:
    def __init__(self, csp):
        self.csp = csp
        self.domain_gen = BaselineDomainGenerator(csp.puzzle)

        self.consistent_assignments = []

        self.__setup_constraints__()

    def __setup_constraints__(self):
        for k in self.csp.puzzle.clues.keys():
            self.csp.add_unary_constraint(k, lambda x: 1 if len(x) - self.csp.puzzle.ans_lens[k] < 2 else 0)

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
                        if n not in dep_graph:
                            dep_graph[n] = set()
                        intersection = self.csp.puzzle.getIntersection(m, n)
                        dep_graph[m].add((n, intersection))
                        dep_graph[n].add((m, intersection))

        def words_intersect(word1, word2, intersection):
            if intersection[0] >= len(word1) or intersection[1] >= len(word2):
                return 0.1
            if word1[intersection[0]] is None or word2[intersection[1]] is None:
                return 1
            return 1 if word1[intersection[0]] == word2[intersection[1]] else 0.1

        for v1 in dep_graph:
            for v2, intersection in dep_graph[v1]:
                self.csp.add_binary_constraint(v1, v2, lambda c1, c2: words_intersect(c1, c2, intersection))

    def __get_hashable(self, assignment):
        return frozenset({(k, v) for k, v in assignment.items()})

    def solve(self):
        domains = self.domain_gen.generate_domains(self.csp.puzzle.clues)
        # consistent_assignments = []

        stack = PriorityQueue()
        assignment = {}
        score = 1
        for key, domain in domains.items():
            stack.push(1/len(domain), key)
        visited = set()
        num_iter = 0
        while len(stack) > 0:
            score, variable = stack.pop()
            # hashable_assignment = self.__get_hashable(assignment)
            if variable in visited:
                print(f'skipping visited assignment')
                print(len(stack))
                continue
            visited.add(variable)
            num_iter += 1
            if assignment.keys() == self.csp.puzzle.clues.keys():
                print(f'found consistent assignment: {assignment}')
                return assignment, score

            # variable = self.csp.get_variable(assignment, domains)
            # updated_domains = set(domains[variable])
            for val in domains[variable]:
                p = self.csp.compute_weight(variable, val, assignment)
                if p == 0:
                    print(f'inconsistent value: {variable}, {val}')
                    # updated_domains.remove(val)
                    # if len(updated_domains) == 0:
                    #     next_assignment = assignment.copy()
                    #     next_assignment[variable] = val
                    #     if self.__get_hashable(next_assignment) not in visited:
                    #         stack.push(score * 0.1, next_assignment)
                    #     print(len(stack))
                    continue

                # next_assignment = assignment.copy()
                # next_assignment[variable] = val
                assignment[variable] = val
                # if self.__get_hashable(next_assignment) not in visited:
                #     stack.push(score * p, next_assignment)
            if num_iter >= utils.MAX_ITER:
                return assignment, score
            print(len(stack))

        return assignment, score