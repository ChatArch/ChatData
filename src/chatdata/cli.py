"""CLI entrypoint for chatdata."""

import click

from chatdata import __version__


@click.group()
@click.version_option(__version__, prog_name="chatdata")
def main() -> None:
    """chatdata command line interface."""
    # Add package-specific commands here. Prefer ChatStyle helpers for
    # interactive input when a command needs recoverable user input.


if __name__ == "__main__":
    main()
