"""Configure a VM or CT with extended options."""

import click
from ..output import output_result


@click.command()
@click.option("--vmid", required=True, type=int, help="VM/CT ID")
@click.option("--node", required=True, help="Node name")
@click.option("--type", "resource_type", type=click.Choice(["qemu", "lxc"]), default="qemu")
# Ressources
@click.option("--memory", type=int, default=None, help="Memory in MB")
@click.option("--cores", type=int, default=None, help="Number of CPU cores")
@click.option("--sockets", type=int, default=None, help="Number of CPU sockets")
# Cloud-Init
@click.option("--ip", default=None, help="IP address in CIDR (e.g. 192.168.1.50/24)")
@click.option("--gw", default=None, help="Gateway IP")
@click.option("--ssh-key", "ssh_key", default=None, help="SSH public key")
@click.option("--nameserver", default=None, help="DNS nameserver")
# Général
@click.option("--description", default=None, help="VM description")
@click.option("--tags", default=None, help="Comma-separated tags")
@click.option("--onboot", type=bool, default=None, help="Start at boot (true/false)")
@click.option("--protection", type=bool, default=None, help="Enable protection (true/false)")
# Réseau
@click.option("--net", "net_config", default=None, help="Network config (e.g. virtio,bridge=vmbr0)")
# Disque
@click.option("--disk", default=None, help="Disk size (e.g. +10G to add 10GB)")
# OS
@click.option("--ostype", default=None, help="OS type (l26, win11, etc.)")
@click.pass_context
def config_vm(ctx, vmid, node, resource_type, memory, cores, sockets,
              ip, gw, ssh_key, nameserver, description, tags, onboot,
              protection, net_config, disk, ostype):
    """Configure a VM or container."""
    proxmox = ctx.obj["api"]
    resource = getattr(proxmox.nodes(node), resource_type)

    params = {}
    changes = []

    # Ressources
    if memory is not None:
        params["memory"] = memory
        changes.append(f"memory={memory}")
    if cores is not None:
        params["cores"] = cores
        changes.append(f"cores={cores}")
    if sockets is not None:
        params["sockets"] = sockets
        changes.append(f"sockets={sockets}")

    # Général
    if description is not None:
        params["description"] = description
        changes.append(f"description={description}")
    if tags is not None:
        params["tags"] = tags
        changes.append(f"tags={tags}")
    if onboot is not None:
        params["onboot"] = 1 if onboot else 0
        changes.append(f"onboot={onboot}")
    if protection is not None:
        params["protection"] = 1 if protection else 0
        changes.append(f"protection={protection}")

    # Réseau / Disque / OS
    if net_config is not None:
        params["net0"] = net_config
        changes.append(f"net0={net_config}")
    if disk is not None:
        params["disk"] = disk
        changes.append(f"disk={disk}")
    if ostype is not None:
        params["ostype"] = ostype
        changes.append(f"ostype={ostype}")

    # Cloud-Init
    if ip is not None:
        params["ipconfig0"] = f"ip={ip}{',gw=' + gw if gw else ''}"
        changes.append(f"ipconfig0={params['ipconfig0']}")
    if ssh_key is not None:
        params["sshkeys"] = ssh_key
        changes.append(f"sshkeys=...")
    if nameserver is not None:
        params["nameserver"] = nameserver
        changes.append(f"nameserver={nameserver}")

    if not params:
        click.echo("No configuration options provided. Use --help for available options.")
        return

    try:
        task = resource(vmid).config.post(**params)
        click.echo(f"Configuration updated for {resource_type} {vmid}.")
        click.echo(f"Changes: {', '.join(changes)}")
        output_result(ctx, {"status": "ok", "task": str(task), "changes": changes})
    except Exception as e:
        click.echo(f"Error configuring {resource_type} {vmid}: {e}", err=True)
