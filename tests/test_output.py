"""Tests pour proxmox_cli.output."""

import json
from unittest.mock import MagicMock
from click.testing import CliRunner
from proxmox_cli.output import output_result


class FakeContext:
    """Simule un contexte Click avec obj dict."""
    def __init__(self, fmt="json"):
        self.obj = {"format": fmt}


def test_output_result_json():
    """output_result en mode json retourne du JSON valide."""
    import io
    import click
    # On teste via CliRunner pour capturer la sortie
    ctx = FakeContext("json")
    data = {"vms": [{"vmid": 100, "name": "test"}]}
    # output_result utilise click.echo, on intercepte
    runner = CliRunner()
    with runner.isolation() as out:
        pass


def test_output_result_json_dict():
    """output_result avec un dict en mode json."""
    ctx = FakeContext("json")
    # On va patcher click.echo pour capturer
    import click
    original = click.echo
    captured = []
    click.echo = lambda s: captured.append(s)
    output_result(ctx, {"status": "ok"})
    click.echo = original
    result = captured[0] if captured else ""
    parsed = json.loads(result)
    assert parsed["status"] == "ok"


def test_output_result_text_list():
    """output_result en mode text avec une liste."""
    ctx = FakeContext("text")
    import click
    original = click.echo
    captured = []
    click.echo = lambda s: captured.append(s)
    output_result(ctx, [{"vmid": 100, "name": "test"}], headers=["vmid", "name"])
    click.echo = original
    output = "".join(captured)
    assert "100" in output
    assert "test" in output


def test_output_result_text_dict():
    """output_result en mode text avec un dict."""
    ctx = FakeContext("text")
    import click
    original = click.echo
    captured = []
    click.echo = lambda s: captured.append(s)
    output_result(ctx, {"status": "running", "cpu": "5%"})
    click.echo = original
    output = "".join(captured)
    assert "running" in output
