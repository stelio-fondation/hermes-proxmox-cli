"""Fixtures partagées pour les tests hermes-proxmox-cli."""

import os
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def clean_env():
    """Nettoie les variables d'environnement avant chaque test."""
    old = {}
    for key in ("PM_URL", "PM_USER", "PM_TOKEN", "PM_VERIFY_SSL"):
        old[key] = os.environ.pop(key, None)
    yield
    for key, val in old.items():
        if val is not None:
            os.environ[key] = val
        else:
            os.environ.pop(key, None)


@pytest.fixture
def mock_proxmox():
    """Retourne un mock de l'API Proxmox."""
    mock = MagicMock()
    mock.nodes.return_value = []
    return mock


@pytest.fixture
def mock_api_client(monkeypatch):
    """Patch proxmoxer.ProxmoxAPI pour retourner un mock."""
    mock = MagicMock()
    monkeypatch.setattr("proxmoxer.ProxmoxAPI", lambda *a, **kw: mock)
    return mock


@pytest.fixture
def pm_env():
    """Configure les variables d'environnement Proxmox."""
    os.environ.update({
        "PM_URL": "https://pve.example.com:8006/api2/json",
        "PM_USER": "root@pam!token",
        "PM_TOKEN": "test-token",
        "PM_VERIFY_SSL": "false",
    })
