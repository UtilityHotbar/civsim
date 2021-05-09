# RPG TOOLS v1.0

import re
import random

DICE_NOTATION = re.compile(r'(\d+)d(\d+)(kh|kl)?(\d+)?')


def roll(dice_string) -> int:
    # Selectively find and replace all instances of dice notation e.g. 3d6 or 2d6kh1
    found_string = DICE_NOTATION.finditer(dice_string)
    for dice in found_string:
        curr = [int(dice.group(1)), int(dice.group(2)), dice.group(3), dice.group(4)] # xdy kh/kl n
        result_list = [random.randint(1, curr[1]) for _ in range(curr[0])]
        if curr[2] == 'kh':
            if curr[3]:
                result_list = sorted(result_list, reverse=True)[0:int(curr[3])]
            else:
                result_list = sorted(result_list, reverse=True)[0:1]
        elif curr[2] == 'kl':
            if curr[3]:
                result_list = sorted(result_list)[0:int(curr[3])]
            else:
                result_list = sorted(result_list)[0:1]
        dice_string = dice_string.replace(dice.group(0), str(sum(result_list)))
    return eval(dice_string)


def generate_menu(options, prompt=None):
    if not prompt:
        print('Your options are:')
    else:
        print(prompt)
    i = 1
    for option in options:
        print(f'{i}. {option}')
        i += 1
    i -= 1
    while True:
        response = input(f'(1-{i}) >> ')
        try:
            response = int(response)
            if not (response >= 1 and response <= i):
                raise ValueError
            break
        except ValueError:
            print(f'Error - Please enter a number from 1 to {i}')
    return options[response-1]
