import utils
from openai import OpenAI
from classes.puzzle import Puzzle
import os

class LLMDomainGenerator:
    def __init__(self, puzzle: Puzzle):
        os.environ["OPENAI_API_KEY"] = utils.OPEN_AI_SECRET_KEY
        self.client = OpenAI(
            organization=utils.OPEN_AI_ORGANIZATION,
            project='$PROJECT_ID'
        )
        self.puzzle = puzzle

        self.role = {"role": "system", "content": "Provide answers to crossword puzzle clues."}


    def generate_domains(self, clues):
        domains = {}
        # for k in clues.keys():
        clue = clues.keys().pop()
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                self.role,
                {
                    "role": "user",
                    "content": f'{self.puzzle.ans_lens[clue]} letter word for {clues[clue]}'
                }
            ],
            logprobs=True,
            top_logprobs=utils.MAX_TOKENS
        )
        print(completion)
        # print(domains)