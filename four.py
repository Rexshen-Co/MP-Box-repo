from datetime import datetime


def show_now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    print(f"Current time: {show_now()}")
