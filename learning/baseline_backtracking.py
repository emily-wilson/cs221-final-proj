from pygame.display import update
from pygame.examples.video import answer

from classes.baseline_domain_generator import BaselineDomainGenerator
import random

class BaselineBacktrackingSearch:
    def __init__(self, csp):
        self.csp = csp
        self.domain_gen = BaselineDomainGenerator(csp.puzzle)

        self.consistent_assignments = []

        self.__setup_constraints__()

    def __setup_constraints__(self):
        # Add unary word length constraints first
        # def fits_length(word, k):
        #     print(f'k: {k}')
        #     print(f'word len: {len(word)}, ans len: {self.csp.puzzle.ans_lens[k]}')
        #     return
        for k in self.csp.puzzle.clues.keys():
            self.csp.add_unary_constraint(k, lambda x: 1 if len(x) - self.csp.puzzle.ans_lens[k] < 2 else 0)
        print(f'has unary constraint for each key: {self.csp.unary_constraints.keys() == self.csp.puzzle.clues.keys()}')

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

        # for v1 in dep_graph:
        #     for v2, intersection in dep_graph[v1]:
        #         self.csp.add_binary_constraint(v1, v2, lambda c1, c2: 1 if (c1[intersection[0]] == c2[intersection[1]] or c1[intersection[0]] is None or c2[intersection[1]] is None) else 0.1)

    def __get_hashable(self, assignment):
        return frozenset({(k, v) for k, v in assignment.items()})

    def solve(self):
        domains = self.domain_gen.generate_domains(self.csp.puzzle.clues)
        consistent_assignments = []

        stack = [({}, 1)]
        visited = set()
        assignment = None
        while len(stack) > 0:
            assignment, score = stack.pop(-1)
            hashable_assignment = self.__get_hashable(assignment)
            if hashable_assignment in visited:
                print(f'skipping visited assignment')
                print(len(stack))
                continue
            visited.add(hashable_assignment)
            if assignment.keys() == self.csp.puzzle.clues.keys():
                print(f'found consistent assignment: {assignment}')
                consistent_assignments.append((assignment, score))
                print(len(stack))
                continue

            variable = self.csp.get_variable(assignment, domains)
            updated_domains = set(domains[variable])
            for val in domains[variable]:
                p = self.csp.compute_weight(variable, val, assignment)
                if p == 0:
                    print(f'inconsistent value: {variable}, {val}')
                    updated_domains.remove(val)
                    if len(updated_domains) == 0:
                        next_assignment = assignment.copy()
                        next_assignment[variable] = val
                        if self.__get_hashable(next_assignment) not in visited:
                            stack.append((next_assignment, score * 0.1))
                        print(len(stack))
                    continue

                next_assignment = assignment.copy()
                next_assignment[variable] = val
                if self.__get_hashable(next_assignment) not in visited:
                    stack.append((next_assignment, score * p))
            print(len(stack))

        return [(assignment, score* 0.1)]