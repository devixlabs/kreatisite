"""Command-line interface for Kreatisite."""

import argparse
import subprocess
import sys
from typing import List, Optional

import yaml

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


def register_domain(args: argparse.Namespace) -> int:
    """Register a domain using AWS Route53."""
    # Verify config file exists
    try:
        with open(args.config_file, 'r') as f:
            yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{args.config_file}' not found", file=sys.stderr)
        return 1
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config file: {str(e)}", file=sys.stderr)
        return 1

    # Build the AWS CLI command using --cli-input-yaml
    cmd = [
        "aws", "route53domains", "register-domain",
        "--domain-name", args.domain_name,
        "--duration-in-years", str(args.duration_in_years),
    ]
    # Auto-renew flag (enabled by default; use --no-auto-renew to disable)
    if args.auto_renew:
        cmd.append("--auto-renew")
    else:
        cmd.append("--no-auto-renew")
    # Always enable privacy protection for contacts
    cmd.append("--privacy-protect-admin-contact")
    cmd.append("--privacy-protect-registrant-contact")
    cmd.append("--privacy-protect-tech-contact")
    # Use YAML file for contact information
    cmd.extend(["--cli-input-yaml", f"file://{args.config_file}"])

    # Execute the command
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(f"Error: {result.stderr.strip()}", file=sys.stderr)
            return 1
        return 0
    except Exception as e:
        print(f"Error executing AWS command: {str(e)}", file=sys.stderr)
        return 1


def create_check_domain_parser(subparsers: argparse._SubParsersAction) -> None:
    """Create the check-domain command parser.

    Args:
        subparsers: The subparser group to add the command to
    """
    check_domain_parser = subparsers.add_parser(
        "check-domain",
        help="Check domain availability using AWS Route53",
    )
    check_domain_parser.add_argument(
        "domain_name",
        help="Domain name to check (e.g., example.com)",
    )


def create_register_domain_parser(subparsers: argparse._SubParsersAction) -> None:
    """Create the register-domain command parser.

    Args:
        subparsers: The subparser group to add the command to
    """
    register_parser = subparsers.add_parser(
        "register-domain",
        help="Register a domain using AWS Route53",
    )
    register_parser.add_argument(
        "domain_name",
        help="Domain name to register (e.g., example.com)",
    )
    register_parser.add_argument(
        "--config-file",
        dest="config_file",
        default="aws-register-domain.yaml",
        help="YAML config file with contact information "
             "(default: aws-register-domain.yaml)",
    )
    register_parser.add_argument(
        "--duration-in-years",
        dest="duration_in_years",
        type=int,
        default=1,
        help="Number of years to register the domain (default: 1)",
    )
    # Auto-renewal is enabled by default; use --no-auto-renew to disable
    register_parser.add_argument(
        "--no-auto-renew",
        dest="auto_renew",
        action="store_false",
        default=True,
        help="Disable auto-renewal (auto-renew is on by default)",
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        argparse.ArgumentParser: The configured parser
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

    # Create command parsers
    create_check_domain_parser(subparsers)
    create_register_domain_parser(subparsers)

    return parser


def main() -> Optional[int]:
    """Run the Kreatisite CLI application.

    Returns:
        Optional[int]: Return code, 0 for success, 1 for failure
    """
    parser = create_parser()

    # Parse arguments
    args = parser.parse_args()

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
