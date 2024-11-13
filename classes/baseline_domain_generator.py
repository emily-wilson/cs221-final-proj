from classes.llm_domain_generator import LLMDomainGenerator
import utils


class BaselineDomainGenerator(LLMDomainGenerator):
    def generate_domains(self, clueKeys, partialAnswers = {}, num_responses = 4):
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
                n = num_responses,
            )
            domains[k] = set()
            for i in range(num_responses):
                content = completion.choices[i].message.content.upper()
                domains[k].add(''.join(letter for letter in content if letter.isalnum()))
        print(domains)
        return domains

    def __get_messages(self, clueKey, prevDomain):
        prompt = {
                    "role": "user",
                    "content": f'{self.puzzle.ans_lens[clueKey]} letter word for \"{self.puzzle.clues[clueKey]}\"'
                }
        responses = [{"role": "assistant", "content": prevResp} for prevResp in prevDomain]
        all_messages = [[prompt, response] for response in responses]
        return [self.role] + [
            m
            for p in all_messages
            for m in p] + [prompt]

    def generate_single_domain(self, clueKey, prevDomain):
        print(f'prompt: {self.puzzle.ans_lens[clueKey]} letter word for \"{self.puzzle.clues[clueKey]}\"')
        domain = set()
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.__get_messages(clueKey, prevDomain),
            n=utils.MAX_TOKENS,
            frequency_penalty=2.0
        )

        for i in range(utils.MAX_TOKENS):
            content = completion.choices[i].message.content.upper()
            domain.add(''.join(letter for letter in content if letter.isalnum()))
        return domain