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


def register_domain(args: argparse.Namespace) -> int:
    """Register a domain using AWS Route53."""
    # Build the AWS CLI command
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
    # Contact info (JSON strings expected)
    cmd.extend(["--admin-contact", args.admin_contact])
    cmd.extend(["--registrant-contact", args.registrant_contact])
    cmd.extend(["--tech-contact", args.tech_contact])
    # Always enable privacy protection for contacts
    cmd.append("--privacy-protect-admin-contact")
    cmd.append("--privacy-protect-registrant-contact")
    cmd.append("--privacy-protect-tech-contact")
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
    # Add the register-domain command
    register_parser = subparsers.add_parser(
        "register-domain",
        help="Register a domain using AWS Route53",
    )
    register_parser.add_argument(
        "domain_name",
        help="Domain name to register (e.g., example.com)",
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
    register_parser.add_argument(
        "--admin-contact",
        dest="admin_contact",
        required=True,
        help="Admin contact info as JSON",
    )
    register_parser.add_argument(
        "--registrant-contact",
        dest="registrant_contact",
        required=True,
        help="Registrant contact info as JSON",
    )
    register_parser.add_argument(
        "--tech-contact",
        dest="tech_contact",
        required=True,
        help="Tech contact info as JSON",
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "help" or not args.command:
        print_help()
        return None
    elif args.command == "check-domain":
        return check_domain_availability(args.domain_name)
    elif args.command == "register-domain":
        return register_domain(args)
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
