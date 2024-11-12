# Example file showing a basic pygame "game loop"
import pygame

import utils
from classes.csp import CSP
from classes.puzzle import Puzzle
from classes.baseline_backtracking import BaselineBacktrackingSearch
import json

# pygame setup
pygame.init()
pygame.font.init()

filename = "data/1-1-2024.json"

puzzle = Puzzle(filename)

screen = pygame.display.set_mode(puzzle.getScreenSize())
clock = pygame.time.Clock()
running = True

csp = CSP(puzzle)
backtracking = BaselineBacktrackingSearch(csp)
assignments = backtracking.solve()

best_assignment = None
for assignment, score in assignments:
    ans_acc, grid_acc = csp.getAccuracy(assignment)
    if best_assignment is None or score > best_assignment[1]:
        best_assignment = (assignment, score)
    print(f'puzzle accuracy: {ans_acc},{grid_acc},{score}')

for k, v in best_assignment[0].items():
    puzzle.answer(k, v)


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

    puzzle.render(screen, word_font, number_font)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(1)  # limits FPS to 60

pygame.quit()