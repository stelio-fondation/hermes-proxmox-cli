import click

@click.command()
@click.option('--node', help='Filter by node name')
@click.option('--type', type=click.Choice(['qemu', 'lxc', 'all']), default='all', help='Resource type')
@click.pass_context
def list_resources(ctx, node, type):
    """List resources available on the Proxmox cluster."""
    proxmox = ctx.obj['api']
    from ..output import output_result

    resources = []
    
    # If no node specified, we might want to list nodes first or crawl all nodes
    # For V1, we list all resources from the cluster perspective
    try:
        data = proxmox.cluster.resources.get(type=type if type != 'all' else None)
        for item in data:
            if node and item.get('node') != node:
                continue
            resources.append({
                'vmid': item.get('vmid'),
                'name': item.get('name'),
                'type': item.get('type'),
                'node': item.get('node'),
                'status': item.get('status'),
                'uptime': item.get('uptime'),
                'cpu': f"{item.get('cpu', 0)*100:.1f}%",
                'mem': f"{item.get('mem', 0)/1024/1024:.0f}MB"
            })
        
        output_result(ctx, resources, headers=['vmid', 'name', 'type', 'node', 'status', 'cpu', 'mem'])
    except Exception as e:
        click.echo(f"Error listing resources: {e}", err=True)
