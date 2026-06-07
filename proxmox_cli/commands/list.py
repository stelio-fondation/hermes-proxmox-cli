"""List resources on the Proxmox cluster with advanced filtering."""

import re
import click
from ..output import output_result


def _parse_filter(filter_str, item):
    """Applique un filtre sur un item. Format: key=value ou key~regex."""
    if "=" in filter_str:
        key, val = filter_str.split("=", 1)
        return str(item.get(key, "")).lower() == val.lower()
    if "~" in filter_str:
        key, val = filter_str.split("~", 1)
        try:
            return bool(re.search(val, str(item.get(key, "")), re.IGNORECASE))
        except re.error:
            return False
    return True


@click.command()
@click.option("--node", help="Filter by node name")
@click.option(
    "--type", "resource_type",
    type=click.Choice(["qemu", "lxc", "all"]),
    default="all",
    help="Resource type",
)
@click.option(
    "--sort",
    type=click.Choice(["vmid", "name", "type", "node", "status", "cpu", "mem"]),
    default="vmid",
    help="Sort resources by field",
)
@click.option(
    "--filter", "filters",
    multiple=True,
    help="Filter resources (key=value or key~regex). Repeatable.",
)
@click.option(
    "--details", is_flag=True, default=False,
    help="Show detailed information (IP, disks, uptime)",
)
@click.pass_context
def list_resources(ctx, node, resource_type, sort, filters, details):
    """List resources available on the Proxmox cluster."""
    proxmox = ctx.obj["api"]

    resources = []
    try:
        data = proxmox.cluster.resources.get(
            type=resource_type if resource_type != "all" else None
        )
        for item in data:
            if node and item.get("node") != node:
                continue

            entry = {
                "vmid": item.get("vmid"),
                "name": item.get("name"),
                "type": item.get("type"),
                "node": item.get("node"),
                "status": item.get("status"),
                "cpu": f"{item.get('cpu', 0) * 100:.1f}%" if item.get("cpu") else "?",
                "mem": f"{item.get('mem', 0) / 1024 / 1024:.0f}MB" if item.get("mem") else "?",
            }

            if details:
                entry["uptime"] = item.get("uptime", "?")
                entry["maxmem"] = f"{item.get('maxmem', 0) / 1024 / 1024:.0f}MB" if item.get("maxmem") else "?"
                entry["maxcpu"] = item.get("maxcpu", "?")
                entry["disk"] = f"{item.get('disk', 0) / 1024 / 1024 / 1024:.1f}GB" if item.get("disk") else "?"
                entry["netout"] = item.get("netout", "?")

            # Apply filters
            if filters:
                if not all(_parse_filter(f, entry) for f in filters):
                    continue

            resources.append(entry)

        # Sort
        sort_key = sort
        reverse = False
        if sort_key == "vmid":
            resources.sort(key=lambda x: x.get("vmid") or 0)
        elif sort_key == "cpu":
            resources.sort(key=lambda x: float(str(x.get("cpu", "0%")).rstrip("%")) or 0, reverse=True)
        elif sort_key == "mem":
            resources.sort(key=lambda x: int(str(x.get("mem", "0MB")).rstrip("MB")) or 0, reverse=True)
        else:
            resources.sort(key=lambda x: str(x.get(sort_key, "")).lower())

        headers = ["vmid", "name", "type", "node", "status", "cpu", "mem"]
        if details:
            headers += ["uptime", "maxcpu", "maxmem", "disk"]

        output_result(ctx, resources, headers=headers)

    except Exception as e:
        click.echo(f"Error listing resources: {e}", err=True)
