import os


def example_task():
    """
    Example task that increments a counter file.\n
    This is a temporary example until we have real tasks. It can be deleted once that happens.
    """
    counter_file = os.path.join(os.path.dirname(__file__), "counter.txt")

    try:
        with open(counter_file, "r") as file:
            counter = int(file.read().strip())
    except FileNotFoundError:
        counter = 0

    counter += 1

    with open(counter_file, "w") as file:
        file.write(str(counter))
