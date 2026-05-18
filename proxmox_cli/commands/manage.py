import click

@click.group()
def manage_vm():
    """Manage VM lifecycle (start, stop, delete)."""
    pass

@manage_vm.command()
@click.option('--vmid', required=True, type=int, help='ID of the VM to start')
@click.option('--node', required=True, help='Node where the VM is located')
@click.pass_context
def start(ctx, vmid, node):
    """Start a VM."""
    proxmox = ctx.obj['api']
    try:
        proxmox.nodes(node).qemu(vmid).status.start.post()
        click.echo(f"VM {vmid} start command sent.")
    except Exception as e:
        click.echo(f"Error starting VM {vmid}: {e}", err=True)

@manage_vm.command()
@click.option('--vmid', required=True, type=int, help='ID of the VM to stop')
@click.option('--node', required=True, help='Node where the VM is located')
@click.pass_context
def stop(ctx, vmid, node):
    """Stop a VM."""
    proxmox = ctx.obj['api']
    try:
        proxmox.nodes(node).qemu(vmid).status.stop.post()
        click.echo(f"VM {vmid} stop command sent.")
    except Exception as e:
        click.echo(f"Error stopping VM {vmid}: {e}", err=True)

@manage_vm.command()
@click.option('--vmid', required=True, type=int, help='ID of the VM to delete')
@click.option('--node', required=True, help='Node where the VM is located')
@click.pass_context
def delete(ctx, vmid, node):
    """Delete a VM."""
    proxmox = ctx.obj['api']
    if click.confirm(f"Are you sure you want to delete VM {vmid} on node {node}?"):
        try:
            proxmox.nodes(node).qemu(vmid).delete()
            click.echo(f"VM {vmid} deleted.")
        except Exception as e:
            click.echo(f"Error deleting VM {vmid}: {e}", err=True)
