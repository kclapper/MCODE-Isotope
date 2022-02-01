import sys

class ProgressTracker:
    """Tracks progress by displaying stdout messages."""

    def __init__(self, stepDescription):
        """Display start of progress message."""

        sys.stdout.write(f"{stepDescription}")
        sys.stdout.flush()

    @classmethod
    def increment(cls):
        """Add . for every iteration of the step."""

        sys.stdout.write(".")
        sys.stdout.flush()

    @classmethod
    def complete(cls):
        """Marks as completed and add newline."""

        sys.stdout.write("Completed\n")
        sys.stdout.flush()