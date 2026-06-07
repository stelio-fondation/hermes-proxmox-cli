import click

@click.group()
def manage_vm():
    """Manage VM lifecycle (start, stop, delete)."""
    pass

@manage_vm.command()
@click.option('--vmid', required=True, type=int, help='ID of the VM/CT to start')
@click.option('--node', required=True, help='Node where the VM/CT is located')
@click.option('--type', 'resource_type', type=click.Choice(['qemu', 'lxc']), default='qemu', help='Resource type (qemu=VM, lxc=container)')
@click.pass_context
def start(ctx, vmid, node, resource_type):
    """Start a VM or container."""
    proxmox = ctx.obj['api']
    try:
        getattr(proxmox.nodes(node), resource_type)(vmid).status.start.post()
        click.echo(f"{resource_type.upper()} {vmid} start command sent.")
    except Exception as e:
        click.echo(f"Error starting {resource_type} {vmid}: {e}", err=True)

@manage_vm.command()
@click.option('--vmid', required=True, type=int, help='ID of the VM/CT to stop')
@click.option('--node', required=True, help='Node where the VM/CT is located')
@click.option('--type', 'resource_type', type=click.Choice(['qemu', 'lxc']), default='qemu', help='Resource type (qemu=VM, lxc=container)')
@click.pass_context
def stop(ctx, vmid, node, resource_type):
    """Stop a VM or container."""
    proxmox = ctx.obj['api']
    try:
        getattr(proxmox.nodes(node), resource_type)(vmid).status.stop.post()
        click.echo(f"{resource_type.upper()} {vmid} stop command sent.")
    except Exception as e:
        click.echo(f"Error stopping {resource_type} {vmid}: {e}", err=True)

@manage_vm.command()
@click.option('--vmid', required=True, type=int, help='ID of the VM/CT to delete')
@click.option('--node', required=True, help='Node where the VM/CT is located')
@click.option('--type', 'resource_type', type=click.Choice(['qemu', 'lxc']), default='qemu', help='Resource type (qemu=VM, lxc=container)')
@click.pass_context
def delete(ctx, vmid, node, resource_type):
    """Delete a VM or container."""
    proxmox = ctx.obj['api']
    if click.confirm(f"Are you sure you want to delete {resource_type} {vmid} on node {node}?"):
        try:
            getattr(proxmox.nodes(node), resource_type)(vmid).delete()
            click.echo(f"{resource_type.upper()} {vmid} deleted.")
        except Exception as e:
            click.echo(f"Error deleting {resource_type} {vmid}: {e}", err=True)
