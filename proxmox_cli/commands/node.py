import click
import time
from datetime import datetime

def _output(ctx, data, headers=None):
    """Utility to output data in text or json format."""
    from ..main import output_result
    output_result(ctx, data, headers)


@click.group()
def node():
    """Gestion locale du nœud Proxmox (hôte hyperviseur)."""
    pass


@node.command()
@click.pass_context
def status(ctx):
    """État global du nœud (uptime, CPU, RAM, load)."""
    proxmox = ctx.obj['api']

    try:
        nodes = proxmox.nodes.get()
        results = []
        for n in nodes:
            node_name = n['node']
            try:
                status_data = proxmox.nodes(node_name).status.get()
            except Exception:
                status_data = {}

            results.append({
                'node': node_name,
                'status': n.get('status', 'unknown'),
                'uptime_sec': status_data.get('uptime', 0),
                'cpu_model': status_data.get('cpuinfo', {}).get('model_name', 'N/A') if isinstance(status_data.get('cpuinfo'), dict) else 'N/A',
                'cpus': status_data.get('cpuinfo', {}).get('cpus', 'N/A') if isinstance(status_data.get('cpuinfo'), dict) else 'N/A',
                'loadavg': status_data.get('loadavg', ['N/A'])[0] if isinstance(status_data.get('loadavg'), list) else 'N/A',
                'memory_total_gb': round(status_data.get('memory', {}).get('total', 0) / 1024 / 1024 / 1024, 1) if isinstance(status_data.get('memory'), dict) else 'N/A',
                'memory_used_gb': round(status_data.get('memory', {}).get('used', 0) / 1024 / 1024 / 1024, 1) if isinstance(status_data.get('memory'), dict) else 'N/A',
                'swap_total_gb': round(status_data.get('swap', {}).get('total', 0) / 1024 / 1024 / 1024, 1) if isinstance(status_data.get('swap'), dict) else 'N/A',
                'swap_used_gb': round(status_data.get('swap', {}).get('used', 0) / 1024 / 1024 / 1024, 1) if isinstance(status_data.get('swap'), dict) else 'N/A',
                'kversion': status_data.get('kversion', 'N/A'),
                'pveversion': status_data.get('pveversion', 'N/A'),
            })

        _output(ctx, results, headers=[
            'node', 'status', 'uptime_sec', 'cpus', 'loadavg',
            'memory_total_gb', 'memory_used_gb',
            'pveversion'
        ])
    except Exception as e:
        click.echo(f"Error getting node status: {e}", err=True)


@node.command(name='info')
@click.option('--node-name', default=None, help='Node name (default: first available)')
@click.pass_context
def node_info(ctx, node_name):
    """Informations détaillées du système (kernel, version PVE, DNS, etc.)."""
    proxmox = ctx.obj['api']

    try:
        if not node_name:
            nodes = proxmox.nodes.get()
            node_name = nodes[0]['node'] if nodes else None

        if not node_name:
            click.echo("No node found.", err=True)
            return

        status_data = proxmox.nodes(node_name).status.get()
        config_data = proxmox.nodes(node_name).config.get() if hasattr(proxmox.nodes(node_name), 'config') else {}

        info = {
            'node': node_name,
            'pveversion': status_data.get('pveversion', 'N/A'),
            'kernel': status_data.get('kversion', 'N/A'),
            'uptime_sec': status_data.get('uptime', 0),
            'cpu_model': status_data.get('cpuinfo', {}).get('model_name', 'N/A') if isinstance(status_data.get('cpuinfo'), dict) else 'N/A',
            'cpus': status_data.get('cpuinfo', {}).get('cpus', 'N/A') if isinstance(status_data.get('cpuinfo'), dict) else 'N/A',
            'cpu_mhz': status_data.get('cpuinfo', {}).get('mhz', 'N/A') if isinstance(status_data.get('cpuinfo'), dict) else 'N/A',
            'load_1min': status_data.get('loadavg', ['N/A'])[0] if isinstance(status_data.get('loadavg'), list) else 'N/A',
            'load_5min': status_data.get('loadavg', ['N/A'])[1] if isinstance(status_data.get('loadavg'), list) and len(status_data.get('loadavg', [])) > 1 else 'N/A',
            'load_15min': status_data.get('loadavg', ['N/A'])[2] if isinstance(status_data.get('loadavg'), list) and len(status_data.get('loadavg', [])) > 2 else 'N/A',
            'memory_total_gb': round(status_data.get('memory', {}).get('total', 0) / 1024 / 1024 / 1024, 1) if isinstance(status_data.get('memory'), dict) else 'N/A',
            'memory_used_gb': round(status_data.get('memory', {}).get('used', 0) / 1024 / 1024 / 1024, 1) if isinstance(status_data.get('memory'), dict) else 'N/A',
            'swap_total_gb': round(status_data.get('swap', {}).get('total', 0) / 1024 / 1024 / 1024, 1) if isinstance(status_data.get('swap'), dict) else 'N/A',
            'swap_used_gb': round(status_data.get('swap', {}).get('used', 0) / 1024 / 1024 / 1024, 1) if isinstance(status_data.get('swap'), dict) else 'N/A',
        }

        _output(ctx, info)
    except Exception as e:
        click.echo(f"Error getting node info: {e}", err=True)


@node.command()
@click.option('--node-name', default=None, help='Node name (default: first available)')
@click.pass_context
def storage(ctx, node_name):
    """Liste les stockages et leur état (usage, type, contenu)."""
    proxmox = ctx.obj['api']

    try:
        if not node_name:
            nodes = proxmox.nodes.get()
            node_name = nodes[0]['node'] if nodes else None

        if not node_name:
            click.echo("No node found.", err=True)
            return

        storages = proxmox.nodes(node_name).storage.get()
        results = []
        for s in storages:
            sid = s.get('storage')
            try:
                content = proxmox.nodes(node_name).storage(sid).status.get()
                used = content[0].get('used', 0) if content else 0
                total = content[0].get('total', 0) if content else 0
                avail = content[0].get('avail', 0) if content else 0
                pct = content[0].get('used_fraction', 0) * 100 if content else 0
            except Exception:
                used = total = avail = pct = 0

            results.append({
                'storage': sid,
                'type': s.get('type', 'N/A'),
                'content': s.get('content', 'N/A'),
                'active': s.get('active', 0),
                'enabled': s.get('enable', 0),
                'total_gb': round(total / 1024 / 1024 / 1024, 1) if total else 0,
                'used_gb': round(used / 1024 / 1024 / 1024, 1) if used else 0,
                'used_pct': f"{pct:.1f}%",
            })

        _output(ctx, results, headers=[
            'storage', 'type', 'content', 'active', 'total_gb', 'used_gb', 'used_pct'
        ])
    except Exception as e:
        click.echo(f"Error listing storage: {e}", err=True)


@node.command()
@click.option('--vmid', required=True, type=int, help='VM ID to backup')
@click.option('--node-name', default=None, help='Node name (default: first available)')
@click.option('--mode', type=click.Choice(['snapshot', 'suspend', 'stop']), default='snapshot', help='Backup mode')
@click.option('--compress', type=click.Choice(['0', '1', 'lzo', 'gzip', 'zstd']), default='zstd', help='Compression algorithm')
@click.pass_context
def backup(ctx, vmid, node_name, mode, compress):
    """Backup une VM via vzdump."""
    proxmox = ctx.obj['api']

    try:
        if not node_name:
            nodes = proxmox.nodes.get()
            node_name = nodes[0]['node'] if nodes else None

        if not node_name:
            click.echo("No node found.", err=True)
            return

        click.echo(f"Starting backup of VM {vmid} on node {node_name} (mode={mode}, compress={compress})...")

        task_upid = proxmox.nodes(node_name).vzdump.post(
            vmid=vmid,
            mode=mode,
            compress=compress
        )

        click.echo(f"Backup task started: {task_upid}")

        # Poll for completion
        while True:
            time.sleep(2)
            task_status = proxmox.nodes(node_name).tasks(task_upid).status.get()
            if task_status.get('status') == 'stopped':
                if task_status.get('exitstatus') == 'OK':
                    click.echo("Backup completed successfully.")
                else:
                    click.echo(f"Backup failed: {task_status.get('exitstatus')}", err=True)
                break

    except Exception as e:
        click.echo(f"Error during backup: {e}", err=True)


@node.command(name='backups')
@click.option('--node-name', default=None, help='Node name (default: first available)')
@click.option('--storage', 'storage_name', default='local', help='Storage to scan for backups')
@click.pass_context
def list_backups(ctx, node_name, storage_name):
    """Liste les backups disponibles sur un stockage."""
    proxmox = ctx.obj['api']

    try:
        if not node_name:
            nodes = proxmox.nodes.get()
            node_name = nodes[0]['node'] if nodes else None

        if not node_name:
            click.echo("No node found.", err=True)
            return

        content = proxmox.nodes(node_name).storage(storage_name).content.get()
        results = []
        for item in content:
            if item.get('content') == 'backup':
                ctime = item.get('ctime', 0)
                results.append({
                    'vmid': item.get('vmid', 'N/A'),
                    'volid': item.get('volid', 'N/A'),
                    'format': item.get('format', 'N/A'),
                    'size_gb': round(item.get('size', 0) / 1024 / 1024 / 1024, 2) if item.get('size') else 0,
                    'date': datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M') if ctime else 'N/A',
                    'notes': item.get('notes', ''),
                })

        if not results:
            click.echo(f"No backups found on {storage_name}.")
            return

        _output(ctx, results, headers=['vmid', 'format', 'size_gb', 'date', 'volid'])
    except Exception as e:
        click.echo(f"Error listing backups: {e}", err=True)


@node.command()
@click.option('--node-name', default=None, help='Node name (default: first available)')
@click.pass_context
def services(ctx, node_name):
    """Liste le statut des services PVE (pveproxy, pvedaemon, etc.)."""
    proxmox = ctx.obj['api']

    try:
        if not node_name:
            nodes = proxmox.nodes.get()
            node_name = nodes[0]['node'] if nodes else None

        if not node_name:
            click.echo("No node found.", err=True)
            return

        svcs = proxmox.nodes(node_name).services.get()
        results = []
        for s in svcs:
            results.append({
                'service': s.get('name', 'N/A'),
                'state': s.get('state', 'N/A'),
                'running': 'yes' if s.get('state') == 'running' else 'no',
                'description': s.get('desc', ''),
            })

        _output(ctx, results, headers=['service', 'state', 'running', 'description'])
    except Exception as e:
        click.echo(f"Error listing services: {e}", err=True)


@node.command()
@click.option('--node-name', default=None, help='Node name (default: first available)')
@click.option('--limit', default=20, type=int, help='Number of tasks to show')
@click.pass_context
def tasks(ctx, node_name, limit):
    """Historique des tâches récentes (clonages, backups, etc.)."""
    proxmox = ctx.obj['api']

    try:
        if not node_name:
            nodes = proxmox.nodes.get()
            node_name = nodes[0]['node'] if nodes else None

        if not node_name:
            click.echo("No node found.", err=True)
            return

        task_list = proxmox.nodes(node_name).tasks.get(limit=limit)
        results = []
        for t in task_list:
            starttime = t.get('starttime', 0)
            endtime = t.get('endtime', 0)
            results.append({
                'upid': t.get('upid', 'N/A'),
                'type': t.get('type', 'N/A'),
                'status': t.get('status', 'N/A'),
                'exitstatus': t.get('exitstatus', 'N/A'),
                'node': t.get('node', 'N/A'),
                'user': t.get('user', 'N/A'),
                'started': datetime.fromtimestamp(starttime).strftime('%Y-%m-%d %H:%M') if starttime else 'N/A',
                'duration_s': round(endtime - starttime, 1) if endtime and starttime else 'N/A',
            })

        if not results:
            click.echo("No tasks found.")
            return

        _output(ctx, results, headers=['type', 'status', 'exitstatus', 'node', 'user', 'started', 'duration_s'])
    except Exception as e:
        click.echo(f"Error listing tasks: {e}", err=True)


@node.command()
@click.option('--node-name', default=None, help='Node name (default: first available)')
@click.pass_context
def network(ctx, node_name):
    """Configuration réseau du nœud (interfaces, bridges, bonds)."""
    proxmox = ctx.obj['api']

    try:
        if not node_name:
            nodes = proxmox.nodes.get()
            node_name = nodes[0]['node'] if nodes else None

        if not node_name:
            click.echo("No node found.", err=True)
            return

        try:
            interfaces = proxmox.nodes(node_name).network.get()
        except Exception:
            click.echo("Network information not available via API.", err=True)
            return

        results = []
        for iface in interfaces:
            results.append({
                'iface': iface.get('iface', 'N/A'),
                'type': iface.get('type', 'N/A'),
                'active': iface.get('active', 0),
                'method': iface.get('method', 'N/A'),
                'address': iface.get('address', 'N/A'),
                'netmask': iface.get('netmask', 'N/A'),
                'gateway': iface.get('gateway', 'N/A'),
                'bridge_ports': iface.get('bridge_ports', ''),
                'bond_mode': iface.get('bond_mode', ''),
            })

        _output(ctx, results, headers=['iface', 'type', 'active', 'method', 'address', 'bridge_ports'])
    except Exception as e:
        click.echo(f"Error listing network: {e}", err=True)


@node.command()
@click.option('--node-name', default=None, help='Node name (default: first available)')
@click.pass_context
def updates(ctx, node_name):
    """Liste les mises à jour disponibles sur le nœud."""
    proxmox = ctx.obj['api']

    try:
        if not node_name:
            nodes = proxmox.nodes.get()
            node_name = nodes[0]['node'] if nodes else None

        if not node_name:
            click.echo("No node found.", err=True)
            return

        try:
            apt_output = proxmox.nodes(node_name).apt.update.get()
        except Exception:
            click.echo("APT update information not available (may need root privileges).", err=True)
            return

        pkgs = apt_output if isinstance(apt_output, list) else []
        results = []
        for p in pkgs:
            if p.get('Status') == 'upgradable' or p.get('Title', ''):
                results.append({
                    'package': p.get('Package', p.get('Title', 'N/A')),
                    'old_version': p.get('OldVersion', 'N/A'),
                    'new_version': p.get('NewVersion', 'N/A'),
                    'urgency': p.get('Urgency', 'N/A'),
                    'title': p.get('Title', ''),
                })

        if not results:
            click.echo("No updates available.")
            return

        _output(ctx, results, headers=['package', 'old_version', 'new_version', 'urgency'])
    except Exception as e:
        click.echo(f"Error checking updates: {e}", err=True)


@node.command()
@click.option('--node-name', default=None, help='Node name (default: first available)')
@click.pass_context
def firewall(ctx, node_name):
    """Liste les règles de pare-feu du nœud."""
    proxmox = ctx.obj['api']

    try:
        if not node_name:
            nodes = proxmox.nodes.get()
            node_name = nodes[0]['node'] if nodes else None

        if not node_name:
            click.echo("No node found.", err=True)
            return

        try:
            rules = proxmox.nodes(node_name).firewall.rules.get()
        except Exception:
            click.echo("Firewall rules not available via API.", err=True)
            return

        results = []
        for r in rules:
            results.append({
                'pos': r.get('pos', 'N/A'),
                'type': r.get('type', 'N/A'),
                'action': r.get('action', 'N/A'),
                'iface': r.get('iface', 'N/A'),
                'proto': r.get('proto', 'N/A'),
                'source': r.get('source', 'N/A'),
                'dest': r.get('dest', 'N/A'),
                'comment': r.get('comment', ''),
                'enable': r.get('enable', 1),
            })

        if not results:
            click.echo("No firewall rules defined.")
            return

        _output(ctx, results, headers=['pos', 'type', 'action', 'iface', 'proto', 'source', 'dest', 'comment'])
    except Exception as e:
        click.echo(f"Error listing firewall rules: {e}", err=True)
