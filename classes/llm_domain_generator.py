import utils
from openai import OpenAI
from classes.puzzle import Puzzle
import os

class LLMDomainGenerator:
    def __init__(self, puzzle: Puzzle):
        os.environ["OPENAI_API_KEY"] = utils.OPEN_AI_SECRET_KEY
        self.client = OpenAI(
            organization=utils.OPEN_AI_ORGANIZATION,
            project='proj_Xi8Kcx1pD0syGhs2B5oGRjED'
        )
        self.puzzle = puzzle

        self.role = {"role": "system", "content": "Provide 1 word answers to crossword puzzle clues."}


    def generate_domains(self, clueKeys, partialAnswers = {}):
        domains = {}
        for k in clueKeys:
            print(f'prompt: {self.puzzle.ans_lens[k]} letter word for \"{self.puzzle.clues[k]}\"')
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    self.role,
                    {
                        "role": "user",
                        "content": f'{self.puzzle.ans_lens[k]} letter word for \"{self.puzzle.clues[k]}\"'
                    }
                ],
                n = utils.MAX_TOKENS,
            )
            domains[k] = set()
            for i in range(utils.MAX_TOKENS):
                content = completion.choices[i].message.content.upper()
                domains[k].add(''.join(letter for letter in content if letter.isalnum()))
        print(domains)
        return domains