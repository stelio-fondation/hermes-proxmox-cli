import click
import time

@click.command()
@click.option('--source-id', required=True, type=int, help='ID of the source VM/Template')
@click.option('--new-id', required=True, type=int, help='ID for the new VM')
@click.option('--name', required=True, help='Name for the new VM')
@click.option('--node', required=True, help='Node where the source is located')
@click.option('--type', 'resource_type', type=click.Choice(['qemu', 'lxc']), default='qemu', help='Resource type (qemu=VM, lxc=container)')
@click.option('--full', is_flag=True, default=False, help='Create a full clone instead of a linked clone')
@click.option('--target-node', default=None, help='Target node to migrate the clone to after creation')
@click.option('--timeout', default=300, type=int, help='Max wait time in seconds for task completion (default: 300)')
@click.pass_context
def clone_vm(ctx, source_id, new_id, name, node, resource_type, full, target_node, timeout):
    """Clone a VM or template."""
    proxmox = ctx.obj['api']
    
    click.echo(f"Cloning {resource_type} {source_id} to {new_id} ({name}) on node {node}...")
    
    try:
        # Clone the VM/CT
        task_upid = getattr(proxmox.nodes(node), resource_type)(source_id).clone.post(
            newid=new_id,
            name=name,
            full=1 if full else 0
        )
        
        click.echo(f"Clone task started: {task_upid}")
        
        # Polling for task completion with timeout
        start_time = time.time()
        clone_ok = False
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                click.echo(f"Clone timed out after {timeout}s.", err=True)
                break
            status = proxmox.nodes(node).tasks(task_upid).status.get()
            if status.get('status') == 'stopped':
                if status.get('exitstatus') == 'OK':
                    click.echo("Clone successful.")
                    clone_ok = True
                else:
                    click.echo(f"Clone failed with status: {status.get('exitstatus')}", err=True)
                break
            time.sleep(2)

        # If a target node is specified (different from source), migrate the clone
        if clone_ok and target_node and target_node != node:
            click.echo(f"Migrating clone {new_id} to node {target_node}...")
            migrate_upid = getattr(proxmox.nodes(node), resource_type)(new_id).migrate.post(target=target_node)
            click.echo(f"Migration task started: {migrate_upid}")

            start_time = time.time()
            while True:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    click.echo(f"Migration timed out after {timeout}s.", err=True)
                    break
                mig_status = proxmox.nodes(node).tasks(migrate_upid).status.get()
                if mig_status.get('status') == 'stopped':
                    if mig_status.get('exitstatus') == 'OK':
                        click.echo("Migration successful.")
                    else:
                        click.echo(f"Migration failed with status: {mig_status.get('exitstatus')}", err=True)
                    break
                time.sleep(2)
            
    except Exception as e:
        click.echo(f"Error cloning VM: {e}", err=True)
