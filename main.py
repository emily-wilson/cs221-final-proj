# Example file showing a basic pygame "game loop"
import pygame

import utils
from classes.csp import CSP
from classes.walksat_csp import WalksatCSP
from classes.puzzle import Puzzle
from learning.a_star import AStarSearch
from learning.basic_backjumping import BasicBackjumping
from learning.baseline import Baseline
from learning.double_backjumping import DoubleBackjumping
from learning.walk_sat import WalkSat
from classes.priority_queue import PriorityQueue
import random
import json

# pygame setup
pygame.init()
pygame.font.init()

mondays = []
with open("data/combined_metadata.json", 'r') as file:
    object = json.load(file)
    mondays = object["Monday"]

baseline_ans_accs = 0
baseline_grid_accs = 0
astar_ans_acc = 0
astar_grid_acc = 0
count = 1

# year = random.randint(2014, 2024)
date = random.choice(mondays)
year = date.split('-')[2]
# filename = f'data/{year}/{date}.json'
filename = f'data/2024/1-1-2024.json'
print(filename)
puzzle = Puzzle(filename)
csp = WalksatCSP(puzzle)

# backjumping = DoubleBackjumping(csp)
walksat = WalkSat(csp)

screen = pygame.display.set_mode(puzzle.getScreenSize())
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    word_font = pygame.font.SysFont("arialunicode", utils.WORD_TEXT_SIZE)
    number_font = pygame.font.SysFont("arialunicode", utils.NUMBER_TEXT_SIZE)

    assignment = walksat.solve_iter()

    if assignment is not None:
        pq = PriorityQueue()
        for k, v in assignment.items():
            p = csp.compute_weight(k, v, assignment)
            pq.push(-p, k)
        while len(pq) > 0:
            p, k = pq.pop()
            print(p, k)
            csp.puzzle.answer(k, assignment[k])
        ans_acc, grid_acc = csp.getAccuracy(assignment)

        print(
            f'Walksat: average grid acc: {grid_acc / count}, average ans acc: {ans_acc / count}, count: {count}')

    puzzle.render(screen, word_font, number_font)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(1)  # limits FPS to 60

pygame.quit()