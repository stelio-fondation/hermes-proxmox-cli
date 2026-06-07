import json
import click


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
