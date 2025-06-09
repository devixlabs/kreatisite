"""Tests for AWS CLI mocking using pytest-subprocess."""

from argparse import Namespace

import pytest

from kreatisite.cmd import check_domain_availability, register_domain


@pytest.mark.unit
def test_check_domain_availability_success(fp):
    """Test check_domain_availability with mocked successful AWS response."""
    fp.register(
        ["aws", "route53domains", "check-domain-availability", "--domain-name", "example.com"],
        stdout='{"Available": true}',
        returncode=0,
    )

    result = check_domain_availability("example.com")

    assert result == 0


@pytest.mark.unit
def test_check_domain_availability_unavailable(fp):
    """Test check_domain_availability with domain unavailable response."""
    fp.register(
        ["aws", "route53domains", "check-domain-availability", "--domain-name", "taken.com"],
        stdout='{"Available": false}',
        returncode=0,
    )

    result = check_domain_availability("taken.com")

    assert result == 0


@pytest.mark.unit
def test_check_domain_availability_aws_error(fp):
    """Test check_domain_availability with AWS CLI error."""
    fp.register(
        ["aws", "route53domains", "check-domain-availability", "--domain-name", "invalid-domain"],
        stderr="An error occurred (ValidationException): Invalid domain",
        returncode=1,
    )

    result = check_domain_availability("invalid-domain")

    assert result == 1


@pytest.mark.unit
def test_check_domain_availability_network_timeout(fp):
    """Test check_domain_availability with network timeout."""
    fp.register(
        ["aws", "route53domains", "check-domain-availability", "--domain-name", "example.com"],
        stderr="Unable to locate credentials",
        returncode=255,
    )

    result = check_domain_availability("example.com")

    assert result == 1


@pytest.mark.unit
def test_register_domain_success(fp, tmp_path):
    """Test register_domain with mocked successful AWS response."""
    # Create a valid config file
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
AdminContact:
  FirstName: John
  LastName: Doe
"""
    )

    fp.register(
        [
            "aws",
            "route53domains",
            "register-domain",
            "--domain-name",
            "example.com",
            "--duration-in-years",
            "1",
            "--auto-renew",
            "--privacy-protect-admin-contact",
            "--privacy-protect-registrant-contact",
            "--privacy-protect-tech-contact",
            "--cli-input-yaml",
            f"file://{config_file}",
        ],
        stdout='{"OperationId": "12345678-1234-1234-1234-123456789012"}',
        returncode=0,
    )

    args = Namespace(
        domain_name="example.com",
        config_file=str(config_file),
        duration_in_years=1,
        auto_renew=True,
    )

    result = register_domain(args)

    assert result == 0


@pytest.mark.unit
def test_register_domain_with_no_auto_renew(fp, tmp_path):
    """Test register_domain with auto-renew disabled."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
AdminContact:
  FirstName: John
  LastName: Doe
"""
    )

    fp.register(
        [
            "aws",
            "route53domains",
            "register-domain",
            "--domain-name",
            "example.com",
            "--duration-in-years",
            "2",
            "--no-auto-renew",
            "--privacy-protect-admin-contact",
            "--privacy-protect-registrant-contact",
            "--privacy-protect-tech-contact",
            "--cli-input-yaml",
            f"file://{config_file}",
        ],
        stdout='{"OperationId": "test-operation-id"}',
        returncode=0,
    )

    args = Namespace(
        domain_name="example.com",
        config_file=str(config_file),
        duration_in_years=2,
        auto_renew=False,
    )

    result = register_domain(args)

    assert result == 0


@pytest.mark.unit
def test_register_domain_aws_error(fp, tmp_path):
    """Test register_domain with AWS CLI error response."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
AdminContact:
  FirstName: John
  LastName: Doe
"""
    )

    fp.register(
        [
            "aws",
            "route53domains",
            "register-domain",
            "--domain-name",
            "invalid.domain",
            "--duration-in-years",
            "1",
            "--auto-renew",
            "--privacy-protect-admin-contact",
            "--privacy-protect-registrant-contact",
            "--privacy-protect-tech-contact",
            "--cli-input-yaml",
            f"file://{config_file}",
        ],
        stderr="An error occurred (InvalidParameterValue): Invalid domain name",
        returncode=1,
    )

    args = Namespace(
        domain_name="invalid.domain",
        config_file=str(config_file),
        duration_in_years=1,
        auto_renew=True,
    )

    result = register_domain(args)

    assert result == 1


@pytest.mark.unit
def test_register_domain_insufficient_permissions(fp, tmp_path):
    """Test register_domain with insufficient AWS permissions."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
AdminContact:
  FirstName: John
  LastName: Doe
"""
    )

    fp.register(
        [
            "aws",
            "route53domains",
            "register-domain",
            "--domain-name",
            "example.com",
            "--duration-in-years",
            "1",
            "--auto-renew",
            "--privacy-protect-admin-contact",
            "--privacy-protect-registrant-contact",
            "--privacy-protect-tech-contact",
            "--cli-input-yaml",
            f"file://{config_file}",
        ],
        stderr="An error occurred (AccessDenied): User is not authorized",
        returncode=1,
    )

    args = Namespace(
        domain_name="example.com",
        config_file=str(config_file),
        duration_in_years=1,
        auto_renew=True,
    )

    result = register_domain(args)

    assert result == 1


@pytest.mark.unit
def test_multiple_aws_calls_in_sequence(fp):
    """Test multiple AWS CLI calls with different responses."""
    # Register multiple calls
    fp.register(
        ["aws", "route53domains", "check-domain-availability", "--domain-name", "available.com"],
        stdout='{"Available": true}',
        returncode=0,
    )

    fp.register(
        ["aws", "route53domains", "check-domain-availability", "--domain-name", "taken.com"],
        stdout='{"Available": false}',
        returncode=0,
    )

    fp.register(
        ["aws", "route53domains", "check-domain-availability", "--domain-name", "error.com"],
        stderr="AWS error",
        returncode=1,
    )

    # Test each call
    assert check_domain_availability("available.com") == 0
    assert check_domain_availability("taken.com") == 0
    assert check_domain_availability("error.com") == 1


@pytest.mark.unit
def test_aws_cli_command_parameters(fp):
    """Test that AWS CLI commands are called with correct parameters."""
    fp.register(
        ["aws", "route53domains", "check-domain-availability", "--domain-name", "test-domain.com"],
        stdout='{"Available": true}',
        returncode=0,
    )

    result = check_domain_availability("test-domain.com")

    assert result == 0
    # The fact that this test passes means the exact command was called
    # pytest-subprocess will fail if the registered command doesn't match exactly
