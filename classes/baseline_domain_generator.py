from classes.llm_domain_generator import LLMDomainGenerator
import utils


class BaselineDomainGenerator(LLMDomainGenerator):
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