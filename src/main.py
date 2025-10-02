from .generator import run_once
from .poster import prepare_post


def main():
    items = run_once()
    for it in items:
        meta = prepare_post(it)
        print("Prepared:", meta)

if __name__ == "__main__":
    main()
