import click

@click.command()
@click.option('--vmid', required=True, type=int, help='ID of the VM to configure')
@click.option('--node', required=True, help='Node where the VM is located')
@click.option('--memory', type=int, help='Memory in MB')
@click.option('--cores', type=int, help='Number of CPU cores')
@click.option('--ip', help='IP address for Cloud-Init (e.g. 192.168.1.50/24)')
@click.option('--gw', help='Gateway for Cloud-Init')
@click.option('--ssh-key', help='Public SSH key for Cloud-Init')
@click.pass_context
def config_vm(ctx, vmid, node, memory, cores, ip, gw, ssh_key):
    """Update VM configuration and Cloud-Init settings."""
    proxmox = ctx.obj['api']
    
    params = {}
    if memory: params['memory'] = memory
    if cores: params['cores'] = cores
    
    # Cloud-Init specific
    if ip:
        params['ipconfig0'] = f"ip={ip},gw={gw}" if gw else f"ip={ip}"
    if ssh_key:
        params['sshkeys'] = ssh_key

    if not params:
        click.echo("No configuration parameters provided.")
        return

    click.echo(f"Updating configuration for VM {vmid} on node {node}...")
    
    try:
        proxmox.nodes(node).qemu(vmid).config.post(**params)
        click.echo("Configuration updated successfully.")
    except Exception as e:
        click.echo(f"Error updating configuration: {e}", err=True)
