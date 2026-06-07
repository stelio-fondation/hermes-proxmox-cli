"""Tests pour les commandes via le CLI principal."""

from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from proxmox_cli.main import cli


def _mock_api():
    """Crée un mock d'API Proxmox complet."""
    mock = MagicMock()
    mock.cluster.resources.get.return_value = []
    qemu_mock = MagicMock()
    mock.nodes.return_value.qemu = qemu_mock
    mock.nodes.return_value.lxc = qemu_mock
    qemu_mock.return_value.clone.post.return_value = "UPID:test"
    qemu_mock.return_value.migrate.post.return_value = "UPID:migrate"
    mock.nodes.return_value.tasks.return_value.status.get.return_value = {
        "status": "stopped", "exitstatus": "OK"
    }
    mock.nodes.return_value.status.get.return_value = {
        "cpuinfo": {"cpus": 8},
        "memory": {"used": 1, "total": 4},
        "loadavg": ["0.5", "0.3", "0.1"],
    }
    mock.nodes.return_value.get.return_value = {
        "node": "gaia", "status": "online", "cpu": 0.1,
    }
    mock.nodes.return_value.storage.get.return_value = []
    mock.nodes.return_value.services.get.return_value = []
    mock.nodes.return_value.tasks.get.return_value = []
    mock.nodes.return_value.network.get.return_value = []
    return mock


def test_list_no_resources():
    """List affiche un résultat vide."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        # --format est une option du groupe parent
        result = runner.invoke(cli, ["--format", "json", "list"])
        assert result.exit_code == 0


def test_list_filter_by_type():
    """List avec --type qemu."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        api = _mock_api()
        api.cluster.resources.get.return_value = [
            {"vmid": 100, "name": "vm1", "type": "qemu", "node": "gaia", "status": "running"},
        ]
        mock_get.return_value = api
        result = runner.invoke(cli, ["--format", "json", "list", "--type", "qemu"])
        assert result.exit_code == 0


def test_list_format_text():
    """List en mode text s'exécute sans erreur."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        api = _mock_api()
        api.cluster.resources.get.return_value = [
            {"vmid": 100, "name": "vm1", "type": "qemu", "node": "gaia", "status": "running"},
        ]
        mock_get.return_value = api
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0


def test_start_vm():
    """manage start démarre une VM."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, ["manage", "start", "--vmid", "100", "--node", "gaia"])
        assert result.exit_code == 0


def test_stop_vm():
    """manage stop arrête une VM."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, ["manage", "stop", "--vmid", "100", "--node", "gaia"])
        assert result.exit_code == 0


def test_stop_vm_force():
    """manage stop --force."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, ["manage", "stop", "--vmid", "100", "--node", "gaia", "--force"])
        assert result.exit_code == 0


def test_delete_vm():
    """manage delete supprime une VM."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, ["manage", "delete", "--vmid", "100", "--node", "gaia"], input="y\n")
        assert result.exit_code == 0


def test_manage_missing_vmid():
    """manage sans --vmid échoue."""
    runner = CliRunner()
    result = runner.invoke(cli, ["manage", "start", "--node", "gaia"])
    assert result.exit_code != 0


def test_clone_basic():
    """Clone basique d'une VM."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, [
            "clone", "--source-id", "100", "--new-id", "101",
            "--node", "gaia", "--name", "my-clone", "--timeout", "2"
        ])
        assert result.exit_code == 0


def test_clone_target_node():
    """Clone vers un autre nœud."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, [
            "clone", "--source-id", "100", "--new-id", "101",
            "--node", "gaia", "--name", "my-clone",
            "--target-node", "zeus", "--timeout", "2"
        ])
        assert result.exit_code == 0


def test_node_status():
    """node status retourne l'état du nœud."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, ["--format", "json", "node", "status"])
        assert result.exit_code == 0


def test_node_info():
    """node info retourne les infos système."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, ["--format", "json", "node", "info"])
        assert result.exit_code == 0


def test_node_storage():
    """node storage liste les stockages."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, ["--format", "json", "node", "storage"])
        assert result.exit_code == 0


def test_node_services():
    """node services liste les services."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, ["--format", "json", "node", "services"])
        assert result.exit_code == 0


def test_node_tasks():
    """node tasks liste les tâches."""
    runner = CliRunner()
    with patch("proxmox_cli.main.get_api_client") as mock_get:
        mock_get.return_value = _mock_api()
        result = runner.invoke(cli, ["--format", "json", "node", "tasks"])
        assert result.exit_code == 0
