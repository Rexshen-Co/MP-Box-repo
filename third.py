import random


def roll_dice() -> int:
    return random.randint(1, 6)


if __name__ == "__main__":
    result = roll_dice()
    print(f"You rolled: {result}")
