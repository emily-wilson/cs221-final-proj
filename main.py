# Example file showing a basic pygame "game loop"
import pygame

import utils
from classes.csp import CSP
from classes.puzzle import Puzzle
from learning.baseline import Baseline
import random

# pygame setup
# pygame.init()
# pygame.font.init()



# screen = pygame.display.set_mode(puzzle.getScreenSize())
# clock = pygame.time.Clock()
# running = True

ans_accs = 0
grid_accs = 0
count = 0
for i in range(1994, 2024):
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
    ans_accs += ans_acc
    grid_accs += grid_acc
    count += 1

print(f'average grid acc: {grid_accs/count}, average ans acc: {ans_accs/count}')

# best_assignment = None
# for assignment, score in assignments:
#     if best_assignment is None or score > best_assignment[1]:
#         best_assignment = (assignment, score)



# while running:
#     # poll for events
#     # pygame.QUIT event means the user clicked X to close your window
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#
#     # fill the screen with a color to wipe away anything from last frame
#     word_font = pygame.font.SysFont("arialunicode", utils.WORD_TEXT_SIZE)
#     number_font = pygame.font.SysFont("arialunicode", utils.NUMBER_TEXT_SIZE)
#
#     text = word_font.render("hello", True, (255, 0, 0))
#     screen.blit(text, (100, 100))
#
#     puzzle.render(screen, word_font, number_font)
#
#     # flip() the display to put your work on screen
#     pygame.display.flip()
#
#     clock.tick(1)  # limits FPS to 60
#
# pygame.quit()