import click
import time

@click.group()
def manage_vm():
    """Manage VM lifecycle (start, stop, delete)."""
    pass

@manage_vm.command()
@click.option('--vmid', required=True, type=int, help='ID of the VM/CT to start')
@click.option('--node', required=True, help='Node where the VM/CT is located')
@click.option('--type', 'resource_type', type=click.Choice(['qemu', 'lxc']), default='qemu', help='Resource type (qemu=VM, lxc=container)')
@click.option('--wait', is_flag=True, default=False, help='Wait for the VM to reach running state (timeout 120s)')
@click.pass_context
def start(ctx, vmid, node, resource_type, wait):
    """Start a VM or container."""
    proxmox = ctx.obj['api']
    resource = getattr(proxmox.nodes(node), resource_type)
    try:
        resource(vmid).status.start.post()
        click.echo(f"{resource_type.upper()} {vmid} start command sent.")
        if wait:
            click.echo(f"Waiting for {resource_type} {vmid} to reach running state...")
            deadline = time.time() + 120
            while time.time() < deadline:
                current = resource(vmid).status.current.get()
                if current.get('status') == 'running':
                    click.echo(f"{resource_type.upper()} {vmid} is now running.")
                    break
                time.sleep(2)
            else:
                click.echo(f"Timeout waiting for {resource_type} {vmid} to start after 120s.", err=True)
    except Exception as e:
        click.echo(f"Error starting {resource_type} {vmid}: {e}", err=True)

@manage_vm.command()
@click.option('--vmid', required=True, type=int, help='ID of the VM/CT to stop')
@click.option('--node', required=True, help='Node where the VM/CT is located')
@click.option('--type', 'resource_type', type=click.Choice(['qemu', 'lxc']), default='qemu', help='Resource type (qemu=VM, lxc=container)')
@click.option('--force', is_flag=True, default=False, help='Force stop (skip graceful shutdown)')
@click.option('--wait', is_flag=True, default=False, help='Wait for the VM to reach stopped state (timeout 120s)')
@click.pass_context
def stop(ctx, vmid, node, resource_type, force, wait):
    """Stop a VM or container (graceful shutdown by default, --force for hard stop)."""
    proxmox = ctx.obj['api']
    resource = getattr(proxmox.nodes(node), resource_type)
    try:
        if force:
            resource(vmid).status.stop.post()
            click.echo(f"{resource_type.upper()} {vmid} hard stop command sent.")
        else:
            resource(vmid).status.shutdown.post()
            click.echo(f"{resource_type.upper()} {vmid} shutdown command sent.")
        if wait:
            click.echo(f"Waiting for {resource_type} {vmid} to stop...")
            deadline = time.time() + 120
            while time.time() < deadline:
                current = resource(vmid).status.current.get()
                if current.get('status') == 'stopped':
                    click.echo(f"{resource_type.upper()} {vmid} is now stopped.")
                    break
                time.sleep(2)
            else:
                click.echo(f"Timeout waiting for {resource_type} {vmid} to stop after 120s.", err=True)
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
