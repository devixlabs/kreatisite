"""Command-line interface for Kreatisite."""

import shutil
import sys
from typing import Optional

# Enforce minimum Python version
if sys.version_info < (3, 9):
    print("Error: Kreatisite requires Python 3.9 or above.", file=sys.stderr)
    sys.exit(1)


from .cmd import check_domain_availability, register_domain
from .parser import create_parser


def check_dependencies() -> None:
    """Check for required external dependencies."""
    required_commands = ["aws"]
    missing = []

    for cmd in required_commands:
        if not shutil.which(cmd):
            missing.append(cmd)

    if missing:
        print(f"Error: Missing required commands: {', '.join(missing)}", file=sys.stderr)
        print("", file=sys.stderr)
        print("To install AWS CLI:", file=sys.stderr)
        print("  Ubuntu/Debian:", file=sys.stderr)
        url = "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        print(f"    {url}", file=sys.stderr)
        print("  Or try: sudo apt install awscli", file=sys.stderr)
        print("", file=sys.stderr)
        print("After installation, configure AWS credentials:", file=sys.stderr)
        print("  aws configure", file=sys.stderr)
        sys.exit(1)


def main() -> Optional[int]:
    """Run the Kreatisite CLI application.

    Returns:
        Optional[int]: Return code, 0 for success, 1 for failure
    """
    parser = create_parser()

    # Parse arguments
    args = parser.parse_args()

    # Check dependencies for AWS commands
    if hasattr(args, "command") and args.command in ["check-domain", "register-domain"]:
        check_dependencies()

    # Command handlers mapping
    command_handlers = {
        "help": lambda _: print_help(),
        "check-domain": lambda args: check_domain_availability(args.domain_name),
        "register-domain": register_domain,
    }

    # Handle commands
    if not args.command or args.command not in command_handlers:
        if not args.command:
            print_help()
        else:
            parser.print_help()
        return None

    # Execute the appropriate handler
    return command_handlers[args.command](args)


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
register-domain  Register a domain using AWS Route53

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
