"""Tests for the cmd module."""

from unittest.mock import Mock, mock_open, patch

from kreatisite.cmd import check_domain_availability, register_domain


@patch("kreatisite.cmd.subprocess.run")
def test_check_domain_availability_success(mock_run, capsys) -> None:
    """Test successful domain availability check."""
    mock_result = Mock()
    mock_result.stdout = '{"Availability": "AVAILABLE"}\n'
    mock_result.stderr = ""
    mock_result.returncode = 0
    mock_run.return_value = mock_result

    result = check_domain_availability("example.com")

    assert result == 0
    captured = capsys.readouterr()
    assert '{"Availability": "AVAILABLE"}' in captured.out
    mock_run.assert_called_once_with(
        ["aws", "route53domains", "check-domain-availability", "--domain-name", "example.com"],
        capture_output=True,
        text=True,
        check=False,
    )


@patch("kreatisite.cmd.subprocess.run")
def test_check_domain_availability_error(mock_run, capsys) -> None:
    """Test domain availability check with AWS error."""
    mock_result = Mock()
    mock_result.stdout = ""
    mock_result.stderr = "An error occurred (AccessDenied)"
    mock_result.returncode = 1
    mock_run.return_value = mock_result

    result = check_domain_availability("example.com")

    assert result == 1
    captured = capsys.readouterr()
    assert "Error: An error occurred (AccessDenied)" in captured.err


@patch("kreatisite.cmd.subprocess.run")
def test_check_domain_availability_exception(mock_run, capsys) -> None:
    """Test domain availability check with subprocess exception."""
    mock_run.side_effect = Exception("Connection error")

    result = check_domain_availability("example.com")

    assert result == 1
    captured = capsys.readouterr()
    assert "Error executing AWS command: Connection error" in captured.err


def test_register_domain_config_file_not_found(capsys) -> None:
    """Test register domain with missing config file."""
    mock_args = Mock()
    mock_args.config_file = "nonexistent.yaml"
    mock_args.domain_name = "example.com"

    result = register_domain(mock_args)

    assert result == 1
    captured = capsys.readouterr()
    assert "Error: Config file 'nonexistent.yaml' not found" in captured.err
    assert "Copy the example file:" in captured.err
    assert "Edit nonexistent.yaml with your information" in captured.err


@patch("builtins.open", mock_open(read_data="invalid: yaml: content: ["))
def test_register_domain_invalid_yaml(capsys) -> None:
    """Test register domain with invalid YAML config."""
    mock_args = Mock()
    mock_args.config_file = "invalid.yaml"
    mock_args.domain_name = "example.com"

    result = register_domain(mock_args)

    assert result == 1
    captured = capsys.readouterr()
    assert "Error parsing YAML config file:" in captured.err


@patch("kreatisite.cmd.subprocess.run")
@patch("builtins.open", mock_open(read_data="AdminContact:\n  FirstName: John"))
def test_register_domain_success(mock_run, capsys) -> None:
    """Test successful domain registration."""
    mock_result = Mock()
    mock_result.stdout = '{"OperationId": "12345"}\n'
    mock_result.stderr = ""
    mock_result.returncode = 0
    mock_run.return_value = mock_result

    mock_args = Mock()
    mock_args.config_file = "config.yaml"
    mock_args.domain_name = "example.com"
    mock_args.duration_in_years = 1
    mock_args.auto_renew = True

    result = register_domain(mock_args)

    assert result == 0
    captured = capsys.readouterr()
    assert '{"OperationId": "12345"}' in captured.out

    # Verify the AWS CLI command was constructed correctly
    expected_cmd = [
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
        "file://config.yaml",
    ]
    mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True, check=False)


@patch("kreatisite.cmd.subprocess.run")
@patch("builtins.open", mock_open(read_data="AdminContact:\n  FirstName: John"))
def test_register_domain_no_auto_renew(mock_run) -> None:
    """Test domain registration with auto-renew disabled."""
    mock_result = Mock()
    mock_result.stdout = ""
    mock_result.stderr = ""
    mock_result.returncode = 0
    mock_run.return_value = mock_result

    mock_args = Mock()
    mock_args.config_file = "config.yaml"
    mock_args.domain_name = "example.com"
    mock_args.duration_in_years = 2
    mock_args.auto_renew = False

    result = register_domain(mock_args)

    assert result == 0

    # Verify --no-auto-renew is used instead of --auto-renew
    expected_cmd = [
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
        "file://config.yaml",
    ]
    mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True, check=False)


@patch("kreatisite.cmd.subprocess.run")
@patch("builtins.open", mock_open(read_data="AdminContact:\n  FirstName: John"))
def test_register_domain_aws_error(mock_run, capsys) -> None:
    """Test domain registration with AWS error."""
    mock_result = Mock()
    mock_result.stdout = ""
    mock_result.stderr = "Domain already exists"
    mock_result.returncode = 1
    mock_run.return_value = mock_result

    mock_args = Mock()
    mock_args.config_file = "config.yaml"
    mock_args.domain_name = "example.com"
    mock_args.duration_in_years = 1
    mock_args.auto_renew = True

    result = register_domain(mock_args)

    assert result == 1
    captured = capsys.readouterr()
    assert "Error: Domain already exists" in captured.err


@patch("kreatisite.cmd.subprocess.run")
@patch("builtins.open", mock_open(read_data="AdminContact:\n  FirstName: John"))
def test_register_domain_subprocess_exception(mock_run, capsys) -> None:
    """Test domain registration with subprocess exception."""
    mock_run.side_effect = Exception("AWS CLI not found")

    mock_args = Mock()
    mock_args.config_file = "config.yaml"
    mock_args.domain_name = "example.com"
    mock_args.duration_in_years = 1
    mock_args.auto_renew = True

    result = register_domain(mock_args)

    assert result == 1
    captured = capsys.readouterr()
    assert "Error executing AWS command: AWS CLI not found" in captured.err
