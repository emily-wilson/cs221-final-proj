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
count = 0
# for i in range(1994, 2024, 40):
filename = f'data/2024/1-1-2024.json'
puzzle = Puzzle(filename)
csp = CSP(puzzle)

    # baseline = Baseline(csp)
    # assignment, score = baseline.solve()
    # print(assignment)
    #
    # for k, v in assignment.items():
    #     puzzle.answer(k, v)
    #
    # ans_acc, grid_acc = csp.getAccuracy(assignment)
    # print(f'puzzle accuracy: {ans_acc},{grid_acc},{score}')
    # baseline_ans_accs += ans_acc
    # baseline_grid_accs += grid_acc
count += 1

backjumping = Backjumping(csp)
assignment = backjumping.solve()
print(assignment)

# for k, v in assignment.items():
#     puzzle.answer(k, v, force_clear=True)

ans_acc, grid_acc = csp.getAccuracy(assignment)
print(f'puzzle accuracy: {ans_acc},{grid_acc}')
astar_ans_acc += ans_acc
astar_grid_acc += grid_acc

# print(f'Baseline: average grid acc: {baseline_grid_accs/count}, average ans acc: {baseline_ans_accs/count}, count: {count}')
print(f'Backjumping: average grid acc: {astar_grid_acc/count}, average ans acc: {astar_ans_acc/count}, count: {count}')

# best_assignment = None
# for assignment, score in assignments:
#     if best_assignment is None or score > best_assignment[1]:
#         best_assignment = (assignment, score)

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

    puzzle.render(screen, word_font, number_font)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(1)  # limits FPS to 60

pygame.quit()