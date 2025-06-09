"""Parser creation functions for Kreatisite CLI."""

import argparse


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
        help="YAML config file with contact information " "(default: aws-register-domain.yaml)",
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
