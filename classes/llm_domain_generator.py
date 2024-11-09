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
        raise NotImplementedError("generate_domains is not implemented in LLMDomainGenerator")