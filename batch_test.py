from classes.csp import CSP
from classes.puzzle import Puzzle
# from learning.basic_backjumping import Backjumping
from learning.double_backjumping import DoubleBackjumping
from learning.baseline import Baseline
import random
import json

day = []
with open("data/combined_metadata.json", 'r') as file:
    object = json.load(file)
    day = object["Monday"]

def test_years(day):
    count = 0
    baseline_ans_accs = 0
    baseline_grid_accs = 0
    backjumping_ans_accs = 0
    backjumping_grid_accs = 0
    for year in range(2004, 2024, 4):
        for i in range(4):
            date = random.choice(day[f'{year}'])
            filename = f'data/{year}/{date}.json'
            puzzle = Puzzle(filename)
            csp = CSP(puzzle)

            baseline = Baseline(csp)
            assignment, score = baseline.solve()
            # print(assignment)

            for k, v in assignment.items():
                puzzle.answer(k, v)

            ans_acc, grid_acc = csp.getAccuracy(assignment)
            # print(f'{year} baseline puzzle accuracy: {ans_acc},{grid_acc}')
            baseline_ans_accs += ans_acc
            baseline_grid_accs += grid_acc
            count += 1

            puzzle = Puzzle(filename)
            csp = CSP(puzzle)
            backjumping = DoubleBackjumping(csp)
            assignment = backjumping.solve()
            # print(assignment)

            # for k, v in assignment.items():
            #     puzzle.answer(k, v, force_clear=True)

            ans_acc, grid_acc = csp.getAccuracy(assignment)
            # print(f'{year} backjumping puzzle accuracy: {ans_acc},{grid_acc}')
            backjumping_ans_accs += ans_acc
            backjumping_grid_accs += grid_acc

        print(f'{year} Baseline: average grid acc: {baseline_grid_accs/count}, average ans acc: {baseline_ans_accs/count}, count: {count}')
        print(f'{year} Backjumping: average grid acc: {backjumping_grid_accs/count}, average ans acc: {backjumping_ans_accs/count}, count: {count}')

def test_temps(day):
    counts = {x: 0 for x in range(20)}
    baseline_ans_accs = {x: 0 for x in range(20)}
    baseline_grid_accs = {x: 0 for x in range(20)}
    backjumping_ans_accs = {x: 0 for x in range(20)}
    backjumping_grid_accs = {x: 0 for x in range(20)}
    year = 2024
    for i in range(4):
        date = random.choice(day[f'{year}'])
        filename = f'data/{year}/{date}.json'
        temp = 18
        # for temp in range(20, 22, 4):
        puzzle = Puzzle(filename)
        csp = CSP(puzzle)

        baseline = Baseline(csp, temperature=temp/10.)
        assignment, score = baseline.solve()
        # print(assignment)

        for k, v in assignment.items():
            puzzle.answer(k, v)

        ans_acc, grid_acc = csp.getAccuracy(assignment)
        print(f'temperature={temp/10.} baseline puzzle accuracy: {ans_acc},{grid_acc}')
        baseline_ans_accs[temp] += ans_acc
        baseline_grid_accs[temp] += grid_acc
        counts[temp] += 1

        puzzle = Puzzle(filename)
        csp = CSP(puzzle)
        backjumping = DoubleBackjumping(csp, temperature=temp/10.)
        assignment = backjumping.solve()
        # print(assignment)

        # for k, v in assignment.items():
        #     puzzle.answer(k, v, force_clear=True)

        ans_acc, grid_acc = csp.getAccuracy(assignment)
        print(f'temperature={temp/10.} backjumping puzzle accuracy: {ans_acc},{grid_acc}')
        backjumping_ans_accs[temp] += ans_acc
        backjumping_grid_accs[temp] += grid_acc

    for temp in baseline_grid_accs.keys():
        if counts[temp] > 0:
            print(
                f'temperature={temp/10.} Baseline: average grid acc: {baseline_grid_accs[temp] / counts[temp]}, average ans acc: {baseline_ans_accs[temp] / counts[temp]}, count: {counts[temp]}')
            print(
                f'temperature={temp/10.} Backjumping: average grid acc: {backjumping_grid_accs[temp] / counts[temp]}, average ans acc: {backjumping_ans_accs[temp] / counts[temp]}, count: {counts[temp]}')

test_years(day)