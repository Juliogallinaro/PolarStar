"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Polar Star."""


if __name__ == "__main__":
    main(prog_name="PolarStar")  # pragma: no cover
