from classes.llm_domain_generator import LLMDomainGenerator
import utils
import math


class BaselineDomainGenerator(LLMDomainGenerator):
    def __init__(self, puzzle):
        super().__init__(puzzle)
        self.prev_messages = {}

    def generate_domains(self, clueKeys, partialAnswers = {}, num_responses = 4):
        domains = {}
        for k in clueKeys:
            message = {
                "role": "user",
                "content": f'{self.puzzle.ans_lens[k]} letter word for \"{self.puzzle.clues[k]}\"'
            }
            self.prev_messages[k] = [message]
            print(f'prompt: {self.puzzle.ans_lens[k]} letter word for \"{self.puzzle.clues[k]}\"')
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    self.role,
                    message
                ],
                n = num_responses,
            )
            domains[k] = set()
            for i in range(num_responses):
                content = completion.choices[i].message.content.upper()
                domains[k].add(''.join(letter for letter in content if letter.isalnum()))
                self.prev_messages[k].append(message)
                self.prev_messages[k].append(completion.choices[i].message)
        # print(domains)
        return domains
        # domains =  {'1a': {'INCUR', 'INCURS'}, '6a': {'AGED', 'OLDER'}, '10a': {'ROLE'}, '14a': {'SCORE'}, '15a': {'CURE', 'CUREY'}, '16a': {'ERAS'}, '17a': {'HONDA'}, '18a': {'IRIS'}, '19a': {'TION', 'FESTY'}, '20a': {'DEADROP', 'TAGGING', 'DUCKDUCKGOOSE'}, '23a': {'STU'}, '25a': {'TU', 'TOI'}, '26a': {'TORSO', 'ABDOMENS', 'ABDOMEN'}, '27a': {'TICKTICKBOOM'}, '31a': {'RATIO'}, '32a': {'LIMBS', 'HIPS', 'ELBOW'}, '33a': {'BAM', 'BANG'}, '36a': {'ALLOY'}, '37a': {'TEXTURES', 'TINTED', 'COATS'}, '39a': {'POLISH', 'POLE'}, '40a': {'PAR'}, '41a': {'ROOK'}, '42a': {'CHAIR', 'CHAIRMAN'}, '43a': {'HOORAY', 'HUZZAH'}, '46a': {'CERTAIN', 'CERTAINLY'}, '49a': {'BOND'}, '50a': {'DSL'}, '51a': {'BALMSPEAK', 'CODDLINGNESS', 'COMFORTING'}, '55a': {'TARIFF', 'FLAT'}, '56a': {'HULA'}, '57a': {'POKES', 'PAWING', 'PICKS'}, '60a': {'OURS', 'OURSY'}, '61a': {'AMPLE', 'QUITE'}, '62a': {'IGLOO', 'CELSIUS', 'GROTTO'}, '63a': {'PLOT', 'RUSE'}, '64a': {'TWEET', 'TRAIN', 'TUNE'}, '65a': {'LAKES'}, '1d': {'LIKE', 'NEAR', 'AKIN', 'MORE'}, '2d': {'RANK'}, '3d': {'CONDUCTOR'}, '4d': {'URDU'}, '5d': {'SHOWNESS', 'SHOWERS', 'SHOWING'}, '6d': {'ACIDIC'}, '7d': {'GURU'}, '8d': {'ERIC'}, '9d': {'WORKSTATION', 'WORKSTATIONS'}, '10d': {'CHANGEE', 'REPENT', 'CHANGEO', 'CHANGE'}, '11d': {'OREOS'}, '12d': {'LASSO'}, '13d': {'FLORENCE', 'SALIDA', 'CRESTA'}, '21d': {'KOI'}, '22d': {'GOOEY', 'GOOP'}, '23d': {'RASHER', 'RASHERS', 'LARDON'}, '24d': {'TIARA'}, '28d': {'CLAN'}, '29d': {'OLIVE'}, '30d': {'ATE', 'BITE'}, '33d': {'MEDITERRANEAN'}, '34d': {'ALIAS'}, '35d': {'MERYL'}, '37d': {'WILCO', 'OSCAR'}, '38d': {'TRA', 'LALA', 'LA'}, '39d': {'PHO'}, '41d': {'IRATE'}, '42d': {'PANELIST'}, '43d': {'HERESY'}, '44d': {'CORSAIR', 'PIRATE'}, '45d': {'SPAD', 'SPADE'}, '46d': {'HONESY', 'STROP'}, '47d': {'UHAUL'}, '48d': {'RETRO'}, '52d': {'HULU'}, '53d': {'ELON'}, '54d': {'OLGA'}, '58d': {'LAMENT', 'GRIEF', 'WOE'}, '59d': {'HELP', 'SAVE'}}
        # for k in domains.keys():
        #     for content in domains[k]:
        #         self.prev_messages[k].append(self.prev_messages[k][0])
        #         self.prev_messages[k].append({"role": "user", "content": content})
        # return domains

    def __get_longest_partial_substring(self, partial):
        substrs = filter(lambda sub: len(sub) > 0, partial.split(' '))
        longest = ''
        for sub in substrs:
            if len(sub) > len(longest):
                longest = sub
        return longest

    def generate_single_domain(self, clueKey, prevDomain, partial_answer=None):
        # print(f'regenerating single domain for \"{self.puzzle.clues[clueKey]}\"')
        # print(self.__get_messages(clueKey, prevDomain))
        domain = set()
        if partial_answer:
            message = {
                "role": "user",
                "content": f'{self.puzzle.ans_lens[clueKey]} letter word for \"{self.puzzle.clues[clueKey]}\" containing the substring \"{self.__get_longest_partial_substring(partial_answer)}\"'
            }
        else:
            message = {
                "role": "user",
                "content": f'{self.puzzle.ans_lens[clueKey]} letter word for \"{self.puzzle.clues[clueKey]}\"'
            }

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.prev_messages[clueKey] + [message],
            n=utils.MAX_RESPONSES,
            max_tokens=int(math.floor(self.puzzle.ans_lens[clueKey]/2)),
            frequency_penalty=2.0,
            temperature=0.75
        )

        for i in range(utils.MAX_RESPONSES):
            content = completion.choices[i].message.content.upper()
            self.prev_messages[clueKey].append(completion.choices[i].message)
            domain.add(''.join(letter for letter in content if letter.isalnum()))
        return domain