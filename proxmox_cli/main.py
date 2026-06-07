import click
from .api import get_api_client

@click.group()
@click.option('--format', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.pass_context
def cli(ctx, format):
    """Proxmox CLI for portable infrastructure automation."""
    ctx.ensure_object(dict)
    ctx.obj['format'] = format
    ctx.obj['api'] = get_api_client()

from .output import output_result

# Import and add commands
from .commands.list import list_resources
from .commands.clone import clone_vm
from .commands.config import config_vm
from .commands.manage import manage_vm
from .commands.node import node as node_group

cli.add_command(list_resources, name='list')
cli.add_command(clone_vm, name='clone')
cli.add_command(config_vm, name='config')
cli.add_command(manage_vm, name='manage')
cli.add_command(node_group, name='node')

if __name__ == '__main__':
    cli(obj={})
