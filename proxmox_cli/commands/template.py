"""Template management for Proxmox."""

import time
import click
from ..output import output_result


@click.group()
def template():
    """Manage VM/CT templates."""
    pass


@template.command("list")
@click.option("--node", default=None, help="Filter by node")
@click.option("--type", "resource_type", type=click.Choice(["qemu", "lxc", "all"]), default="all")
@click.pass_context
def template_list(ctx, node, resource_type):
    """List available templates."""
    proxmox = ctx.obj["api"]
    try:
        data = proxmox.cluster.resources.get(
            type=resource_type if resource_type != "all" else None
        )
        templates = []
        for item in data:
            if item.get("template") != 1:
                continue
            if node and item.get("node") != node:
                continue
            templates.append({
                "vmid": item.get("vmid"),
                "name": item.get("name"),
                "type": item.get("type"),
                "node": item.get("node"),
                "size": f"{item.get('maxdisk', 0) / 1024 / 1024 / 1024:.1f}GB" if item.get("maxdisk") else "?",
            })
        output_result(ctx, templates, headers=["vmid", "name", "type", "node", "size"])
    except Exception as e:
        click.echo(f"Error listing templates: {e}", err=True)


@template.command("deploy")
@click.option("--source-id", required=True, type=int, help="Template VMID")
@click.option("--new-id", required=True, type=int, help="New VM/CT ID")
@click.option("--name", required=True, help="Name for the new VM/CT")
@click.option("--node", required=True, help="Target node")
@click.option("--type", "resource_type", type=click.Choice(["qemu", "lxc"]), default="qemu")
@click.option("--memory", type=int, default=None, help="Memory in MB")
@click.option("--cores", type=int, default=None, help="CPU cores")
@click.option("--storage", default=None, help="Target storage")
@click.option("--timeout", default=300, type=int, help="Max wait time in seconds")
@click.pass_context
def template_deploy(ctx, source_id, new_id, name, node, resource_type, memory, cores, storage, timeout):
    """Deploy a VM/CT from a template."""
    proxmox = ctx.obj["api"]
    resource = getattr(proxmox.nodes(node), resource_type)

    try:
        clone_params = {"newid": new_id, "name": name}
        task = resource(source_id).clone.post(**clone_params)
        click.echo(f"Deploy started. Task: {task}")

        # Wait for clone
        start = time.time()
        while time.time() - start < timeout:
            status = proxmox.nodes(node).tasks(task).status.get()
            if status.get("status") == "stopped":
                if status.get("exitstatus") == "OK":
                    click.echo("Deploy successful.")
                else:
                    click.echo(f"Deploy failed: {status.get('exitstatus')}", err=True)
                break
            time.sleep(2)
        else:
            click.echo(f"Deploy timed out after {timeout}s.", err=True)
            return

        # Apply config overrides
        if memory:
            resource(new_id).config.post(memory=memory)
            click.echo(f"Memory set to {memory}MB")
        if cores:
            resource(new_id).config.post(cores=cores)
            click.echo(f"CPU cores set to {cores}")

    except Exception as e:
        click.echo(f"Error deploying template: {e}", err=True)


@template.command("convert")
@click.option("--vmid", required=True, type=int, help="VM/CT ID to convert")
@click.option("--node", required=True, help="Node name")
@click.option("--type", "resource_type", type=click.Choice(["qemu", "lxc"]), default="qemu")
@click.option("--force", is_flag=True, default=False, help="Skip confirmation")
@click.pass_context
def template_convert(ctx, vmid, node, resource_type, force):
    """Convert a VM/CT into a template."""
    if not force:
        if not click.confirm(f"Convert {resource_type} {vmid} to template? This is irreversible!"):
            return
    proxmox = ctx.obj["api"]
    try:
        resource = getattr(proxmox.nodes(node), resource_type)
        task = resource(vmid).template.post()
        click.echo(f"Converting {resource_type} {vmid} to template. Task: {task}")
    except Exception as e:
        click.echo(f"Error converting to template: {e}", err=True)
