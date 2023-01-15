"""Guess a number game:

Computer generates a random integer and tries to guess that integer in
a minimum number of tries possible.
"""

import numpy as np


def random_predict_midl(number: int = np.random.randint(1, 101)) -> int:
    """Find a random number

    Args:
        number (int, optional): Number to find. Should be in range 1-100.
        Defaults to randomly generated number.

    Returns:
        int: Number of cycles/tries
    """

    if number not in range(1, 101):  # protection form a wrong input
        raise ValueError('Number not in range!')

    minimum, maximum = 1, 101  # set minimum and maximum numbers in range.
    count = 0  # number of tries

    while True:
        count += 1
        midl = (minimum + maximum) // 2

        if midl > number:
            maximum = midl

        elif midl < number:
            minimum = midl

        else:
            return count


def score_game_midl(func) -> int:
    """Benchmark, how much tries does our algorythm need to solve a task.

    Args:
        random_predict_midl (): prediction fuction

    Returns:
        int: mean number of tries
    """

    count_ls = []
    np.random.seed(1)  # fixed random seed for constancy.
    random_array = np.random.randint(1, 101, size=(1000))  # list of integers

    for number in random_array:
        count_ls.append(func(number))

    score = int(np.mean(count_ls))

    print(f"Your algorithm can solve a task in {score} tries average.")

    return score


if __name__ == "__main__":
    # RUN
    score_game_midl(random_predict_midl)
