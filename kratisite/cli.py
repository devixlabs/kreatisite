"""Command-line interface for KratiSite."""

import argparse
import sys


def main():
    """Run the KratiSite CLI application."""
    parser = argparse.ArgumentParser(
        prog="kratisite",
        description="KratiSite - A command line application",
        epilog="For more information, visit https://devixlabs.com",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add the help command
    help_parser = subparsers.add_parser("help", help="Display detailed help information")

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "help" or not args.command:
        print_help()
    else:
        parser.print_help()


def print_help():
    """Print detailed help information."""
    help_text = """
KratiSite Command Line Application
=================================

DESCRIPTION
-----------
KratiSite is a powerful command line tool designed to help you manage your tasks.

USAGE
-----
kratisite [command] [options]

COMMANDS
--------
help        Display this detailed help information

EXAMPLES
--------
# Display help
kratisite help

NOTES
-----
This is an initial version of the application. More features will be added in the future.
"""
    print(help_text)


if __name__ == "__main__":
    main()