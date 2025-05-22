"""Command-line interface for Kreatisite."""

import argparse
import subprocess
import sys
from typing import List, Optional

# Enforce minimum Python version
if sys.version_info < (3, 9):
    print("Error: Kreatisite requires Python 3.9 or above.", file=sys.stderr)
    sys.exit(1)


def check_domain_availability(domain_name: str) -> int:
    """Check domain availability using AWS Route53.

    Args:
        domain_name: The domain name to check.

    Returns:
        int: 0 for success, 1 for failure
    """
    cmd: List[str] = [
        "aws",
        "route53domains",
        "check-domain-availability",
        "--domain-name",
        domain_name,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        # Print the stdout result
        if result.stdout:
            print(result.stdout.strip())

        # Signal to the user if there was an error
        if result.stderr:
            print(f"Error: {result.stderr.strip()}", file=sys.stderr)
            return 1

        return 0
    except Exception as e:
        print(f"Error executing AWS command: {str(e)}", file=sys.stderr)
        return 1


def main() -> Optional[int]:
    """Run the Kreatisite CLI application.

    Returns:
        Optional[int]: Return code, 0 for success, 1 for failure
    """
    parser = argparse.ArgumentParser(
        prog="kreatisite",
        description="Kreatisite - A command line application",
        epilog="For more information, visit https://devixlabs.com",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add the help command
    subparsers.add_parser(
        "help",
        help="Display detailed help information",
    )

    # Add the check-domain command
    check_domain_parser = subparsers.add_parser(
        "check-domain",
        help="Check domain availability using AWS Route53",
    )
    check_domain_parser.add_argument(
        "domain_name",
        help="Domain name to check (e.g., example.com)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "help" or not args.command:
        print_help()
        return None
    elif args.command == "check-domain":
        return check_domain_availability(args.domain_name)
    else:
        parser.print_help()
        return None


def print_help() -> None:
    """Print detailed help information."""
    help_text = """
Kreatisite Command Line Application
=================================

DESCRIPTION
-----------
Kreatisite is a powerful command line tool designed to help you manage
your tasks.

USAGE
-----
kreatisite [command] [options]

COMMANDS
--------
help            Display this detailed help information
check-domain    Check domain availability using AWS Route53

EXAMPLES
--------
# Display help
kreatisite help

# Check domain availability
kreatisite check-domain example.com

NOTES
-----
This is an initial version of the application.
More features will be added in the future.
"""
    print(help_text)


if __name__ == "__main__":
    main()
