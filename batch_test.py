from classes.csp import CSP
from classes.puzzle import Puzzle
from learning.backjumping import Backjumping
from learning.baseline import Baseline
import random

count = 0
baseline_ans_accs = 0
baseline_grid_accs = 0
backjumping_ans_accs = 0
backjumping_grid_accs = 0
for i in range(1994, 2024, 40):
    filename = f'data/{i}/{random.randint(1, 12)}-{random.randint(1, 28)}-{i}.json'
    puzzle = Puzzle(filename)
    csp = CSP(puzzle)

    baseline = Baseline(csp)
    assignment, score = baseline.solve()
    print(assignment)

    for k, v in assignment.items():
        puzzle.answer(k, v)

    ans_acc, grid_acc = csp.getAccuracy(assignment)
    print(f'puzzle accuracy: {ans_acc},{grid_acc},{score}')
    baseline_ans_accs += ans_acc
    baseline_grid_accs += grid_acc
    count += 1

    backjumping = Backjumping(csp)
    assignment = backjumping.solve()
    print(assignment)

    for k, v in assignment.items():
        puzzle.answer(k, v, force_clear=True)

    ans_acc, grid_acc = csp.getAccuracy(assignment)
    print(f'puzzle accuracy: {ans_acc},{grid_acc}')
    backjumping_ans_accs += ans_acc
    backjumping_grid_accs += grid_acc

print(f'Baseline: average grid acc: {baseline_grid_accs/count}, average ans acc: {baseline_ans_accs/count}, count: {count}')
print(f'Backjumping: average grid acc: {backjumping_grid_accs/count}, average ans acc: {backjumping_ans_accs/count}, count: {count}')