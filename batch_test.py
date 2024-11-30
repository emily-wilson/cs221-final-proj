from classes.csp import CSP
from classes.puzzle import Puzzle
# from learning.basic_backjumping import Backjumping
from learning.double_backjumping import DoubleBackjumping
from learning.baseline import Baseline
import random
import json

count = 0
baseline_ans_accs = 0
baseline_grid_accs = 0
backjumping_ans_accs = 0
backjumping_grid_accs = 0

mondays = []
with open("data/combined_metadata.json", 'r') as file:
    object = json.load(file)
    mondays = object["Monday"]

visited_years = set()
while len(visited_years) < 1:
    date = random.choice(mondays)
    year = date.split('-')[2]
    if year in visited_years:
        continue
    visited_years.add(year)
    filename = f'data/{year}/{date}.json'
    puzzle = Puzzle(filename)
    csp = CSP(puzzle)

    baseline = Baseline(csp)
    assignment, score = baseline.solve()
    # print(assignment)

    for k, v in assignment.items():
        puzzle.answer(k, v)

    ans_acc, grid_acc = csp.getAccuracy(assignment)
    print(f'{year} baseline puzzle accuracy: {ans_acc},{grid_acc}')
    baseline_ans_accs += ans_acc
    baseline_grid_accs += grid_acc
    count += 1

    puzzle = Puzzle(filename)
    backjumping = DoubleBackjumping(csp)
    assignment = backjumping.solve()
    # print(assignment)

    # for k, v in assignment.items():
    #     puzzle.answer(k, v, force_clear=True)

    ans_acc, grid_acc = csp.getAccuracy(assignment)
    print(f'{year} backjumping puzzle accuracy: {ans_acc},{grid_acc}')
    backjumping_ans_accs += ans_acc
    backjumping_grid_accs += grid_acc

print(f'Baseline: average grid acc: {baseline_grid_accs/count}, average ans acc: {baseline_ans_accs/count}, count: {count}')
print(f'Backjumping: average grid acc: {backjumping_grid_accs/count}, average ans acc: {backjumping_ans_accs/count}, count: {count}')