from classes.csp import CSP

class WalksatCSP(CSP):
    def __init__(self, puzzle):
        super().__init__(puzzle)

    def compute_weight(self, var, val, assignment, sum_bin_constraints=False, count_empties=True, flagged_answers = set()):
        weight = 0
        if var in self.unary_constraints:
            for f in self.unary_constraints[var]:
                weight += f(val)
        if var in self.binary_constraints:
            binary_constraints = self.binary_constraints[var]
            for k, f in binary_constraints:
                if k not in assignment:
                    continue
                weight += f(val, assignment[k])
        # print(f'var: {var}, val: {val}, sum: {bin_const_sum}')
        return weight