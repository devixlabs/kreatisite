"""Command functions for Kreatisite CLI."""

import subprocess
import sys
from typing import List

import yaml
import argparse


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
