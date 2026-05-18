import click
import json
import sys
from .api import get_api_client

@click.group()
@click.option('--format', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.pass_context
def cli(ctx, format):
    """Proxmox CLI for portable infrastructure automation."""
    ctx.ensure_object(dict)
    ctx.obj['format'] = format
    ctx.obj['api'] = get_api_client()

def output_result(ctx, data, headers=None):
    """Utility to output data in text or json format."""
    format_type = ctx.obj.get('format', 'text')
    if format_type == 'json':
        click.echo(json.dumps(data, indent=2))
    else:
        if isinstance(data, list) and data:
            if not headers:
                headers = data[0].keys()
            # Simple tabular output
            header_str = " | ".join(str(h).upper() for h in headers)
            click.echo(header_str)
            click.echo("-" * len(header_str))
            for item in data:
                row = " | ".join(str(item.get(h, "")) for h in headers)
                click.echo(row)
        elif isinstance(data, dict):
            for k, v in data.items():
                click.echo(f"{k}: {v}")
        else:
            click.echo(data)

# Import and add commands
from .commands.list import list_resources
from .commands.clone import clone_vm
from .commands.config import config_vm
from .commands.manage import manage_vm

cli.add_command(list_resources, name='list')
cli.add_command(clone_vm, name='clone')
cli.add_command(config_vm, name='config')
cli.add_command(manage_vm, name='manage')

if __name__ == '__main__':
    cli(obj={})
