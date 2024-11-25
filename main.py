# Example file showing a basic pygame "game loop"
import pygame

import utils
from classes.csp import CSP
from classes.puzzle import Puzzle
from learning.a_star import AStarSearch
from learning.backjumping import Backjumping
from learning.baseline import Baseline
import random

# pygame setup
pygame.init()
pygame.font.init()

baseline_ans_accs = 0
baseline_grid_accs = 0
astar_ans_acc = 0
astar_grid_acc = 0
count = 1

year = random.randint(1994, 2024)
filename = f'data/{year}/{random.randint(1, 12)}-{random.randint(1, 28)}-{year}.json'
print(filename)
puzzle = Puzzle(filename)
csp = CSP(puzzle)

backjumping = Backjumping(csp)

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

    text = word_font.render("hello", True, (255, 0, 0))
    screen.blit(text, (100, 100))

    assignment = backjumping.solve_iter()

    if assignment is not None:
        ans_acc, grid_acc = csp.getAccuracy(assignment)
        print(f'puzzle accuracy: {ans_acc},{grid_acc}')

        print(
            f'Backjumping: average grid acc: {grid_acc / count}, average ans acc: {ans_acc / count}, count: {count}')

    puzzle.render(screen, word_font, number_font)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(1)  # limits FPS to 60

pygame.quit()