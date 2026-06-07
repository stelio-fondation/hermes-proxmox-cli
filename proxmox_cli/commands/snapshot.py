"""VM/CT Snapshot management."""

import click
from ..output import output_result


@click.group()
def snapshot():
    """Manage VM/CT snapshots."""
    pass


@snapshot.command("list")
@click.option("--vmid", required=True, type=int, help="VM/CT ID")
@click.option("--node", required=True, help="Node name")
@click.option("--type", "resource_type", type=click.Choice(["qemu", "lxc"]), default="qemu")
@click.pass_context
def snapshot_list(ctx, vmid, node, resource_type):
    """List snapshots for a VM/CT."""
    proxmox = ctx.obj["api"]
    try:
        resource = getattr(proxmox.nodes(node), resource_type)
        data = resource(vmid).snapshot.get()
        result = []
        for snap in data:
            result.append({
                "name": snap.get("name"),
                "description": snap.get("description", ""),
                "snaptime": snap.get("snaptime", ""),
                "parent": snap.get("parent", ""),
            })
        output_result(ctx, result, headers=["name", "description", "snaptime", "parent"])
    except Exception as e:
        click.echo(f"Error listing snapshots: {e}", err=True)


@snapshot.command("create")
@click.option("--vmid", required=True, type=int, help="VM/CT ID")
@click.option("--node", required=True, help="Node name")
@click.option("--name", "snapname", required=True, help="Snapshot name")
@click.option("--description", default="", help="Snapshot description")
@click.option("--type", "resource_type", type=click.Choice(["qemu", "lxc"]), default="qemu")
@click.pass_context
def snapshot_create(ctx, vmid, node, snapname, description, resource_type):
    """Create a new snapshot."""
    proxmox = ctx.obj["api"]
    try:
        resource = getattr(proxmox.nodes(node), resource_type)
        params = {"snapname": snapname}
        if description:
            params["description"] = description
        task = resource(vmid).snapshot.post(**params)
        click.echo(f"Snapshot '{snapname}' created. Task: {task}")
    except Exception as e:
        click.echo(f"Error creating snapshot: {e}", err=True)


@snapshot.command("rollback")
@click.option("--vmid", required=True, type=int, help="VM/CT ID")
@click.option("--node", required=True, help="Node name")
@click.option("--name", "snapname", required=True, help="Snapshot name to rollback to")
@click.option("--type", "resource_type", type=click.Choice(["qemu", "lxc"]), default="qemu")
@click.pass_context
def snapshot_rollback(ctx, vmid, node, snapname, resource_type):
    """Rollback to a snapshot."""
    proxmox = ctx.obj["api"]
    try:
        resource = getattr(proxmox.nodes(node), resource_type)
        task = resource(vmid).snapshot(snapname).rollback.post()
        click.echo(f"Rollback to '{snapname}' started. Task: {task}")
    except Exception as e:
        click.echo(f"Error rolling back: {e}", err=True)


@snapshot.command("delete")
@click.option("--vmid", required=True, type=int, help="VM/CT ID")
@click.option("--node", required=True, help="Node name")
@click.option("--name", "snapname", required=True, help="Snapshot name to delete")
@click.option("--type", "resource_type", type=click.Choice(["qemu", "lxc"]), default="qemu")
@click.option("--force", is_flag=True, default=False, help="Skip confirmation")
@click.pass_context
def snapshot_delete(ctx, vmid, node, snapname, resource_type, force):
    """Delete a snapshot."""
    if not force:
        if not click.confirm(f"Delete snapshot '{snapname}' on {resource_type} {vmid}?"):
            return
    proxmox = ctx.obj["api"]
    try:
        resource = getattr(proxmox.nodes(node), resource_type)
        task = resource(vmid).snapshot(snapname).delete.request("DELETE")
        click.echo(f"Snapshot '{snapname}' deleted.")
    except Exception as e:
        click.echo(f"Error deleting snapshot: {e}", err=True)
