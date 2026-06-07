"""Tests pour proxmox_cli.api."""

import os
import pytest
from unittest.mock import patch, MagicMock
import click
from proxmox_cli.api import get_api_client


def test_get_api_client_with_env():
    """Crée un client avec les variables d'environnement."""
    os.environ.update({
        "PM_URL": "https://pve.example.com:8006/api2/json",
        "PM_USER": "root@pam!token",
        "PM_TOKEN": "test-token",
        "PM_VERIFY_SSL": "false",
    })
    with patch("proxmox_cli.api.ProxmoxAPI") as mock_proxmox:
        client = get_api_client()
        mock_proxmox.assert_called_once()
        args, kwargs = mock_proxmox.call_args
        assert "pve.example.com" in args[0]
        assert kwargs["user"] == "root@pam"
        assert kwargs["token_name"] == "token"
        assert kwargs["token_value"] == "test-token"
        assert kwargs["verify_ssl"] is False


def test_get_api_client_missing_url():
    """Lève une erreur si PM_URL est manquant."""
    os.environ["PM_URL"] = ""
    with pytest.raises(click.ClickException, match="PM_URL"):
        get_api_client()


def test_get_api_client_missing_user():
    """Lève une erreur si PM_USER est manquant."""
    os.environ.update({
        "PM_URL": "https://pve.example.com:8006/api2/json",
        "PM_USER": "",
        "PM_TOKEN": "test-token",
    })
    with pytest.raises(click.ClickException):
        get_api_client()


def test_get_api_client_verify_ssl_true():
    """Respecte PM_VERIFY_SSL=true."""
    os.environ.update({
        "PM_URL": "https://pve.example.com:8006/api2/json",
        "PM_USER": "root@pam!token",
        "PM_TOKEN": "test-token",
        "PM_VERIFY_SSL": "true",
    })
    with patch("proxmox_cli.api.ProxmoxAPI") as mock_proxmox:
        get_api_client()
        mock_proxmox.assert_called_once()
        _, kwargs = mock_proxmox.call_args
        assert kwargs.get("verify_ssl") is True


def test_get_api_client_parses_user_parts():
    """Parse correctement PM_USER en user et token_name."""
    os.environ.update({
        "PM_URL": "https://pve.example.com:8006/api2/json",
        "PM_USER": "admin@pve!my-token-id",
        "PM_TOKEN": "secret",
    })
    with patch("proxmox_cli.api.ProxmoxAPI") as mock_proxmox:
        get_api_client()
        _, kwargs = mock_proxmox.call_args
        assert kwargs["user"] == "admin@pve"
        assert kwargs["token_name"] == "my-token-id"
