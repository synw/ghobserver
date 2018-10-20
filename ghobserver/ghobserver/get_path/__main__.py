import os
import ghobserver


def get_path():
    return os.path.dirname(os.path.realpath(ghobserver.__file__))


if __name__ == "__main__":
    print(get_path())
