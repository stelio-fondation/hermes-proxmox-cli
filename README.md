# hermes-proxmox-cli
[![CI](https://github.com/stelio-fondation/hermes-proxmox-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/stelio-fondation/hermes-proxmox-cli/actions)

CLI de pilotage d'infrastructure Proxmox — gestion des VMs/CTs et administration du nœud hyperviseur.
Conçu pour les humains et les agents IA (Hermes Agent, Claude Code, etc.).

## Installation

```bash
uv sync
```

## Configuration

Variables d'environnement :

```bash
export PM_URL="https://your-proxmox-ip:8006/api2/json"
export PM_USER="root@pam!mytokenid"
export PM_TOKEN="your-api-token-secret"
export PM_VERIFY_SSL="false"
```

## Commandes disponibles

Toutes les commandes supportent `--format json` (ou `text` par défaut) pour l'intégration IA.

### Gestion des VMs / CTs

| Commande | Description |
|---|---|
| `list [--node <nom>] [--type qemu\|lxc\|all]` | Lister les ressources du cluster |
| `clone --source-id <id> --new-id <id> --name <nom> --node <nom>` | Cloner une VM/template |
| `config --vmid <id> --node <nom> [options]` | Configurer une VM (mémoire, CPU, Cloud-Init) |
| `manage start --vmid <id> --node <nom>` | Démarrer une VM |
| `manage stop --vmid <id> --node <nom>` | Arrêter une VM |
| `manage delete --vmid <id> --node <nom>` | Supprimer une VM |

**Options de config :**
- `--memory <MB>` — Mémoire vive
- `--cores <N>` — Nombre de CPU
- `--ip <CIDR>` — Adresse IP Cloud-Init (ex: `192.168.1.50/24`)
- `--gw <IP>` — Passerelle Cloud-Init
- `--ssh-key "<key>"` — Clé SSH publique Cloud-Init

### Administration du nœud hyperviseur

| Commande | Description |
|---|---|
| `node status` | **État global du nœud** — uptime, CPU, RAM, load, version PVE |
| `node info` | **Infos système détaillées** — kernel, modèle CPU, swap, loads 1/5/15min |
| `node storage` | **Stockages** — liste, type, actif, espace utilisé/total |
| `node services` | **Services PVE** — pveproxy, pvedaemon, corosync, etc. |
| `node tasks [--limit <N>]` | **Tâches récentes** — clonages, backups, migrations |
| `node network` | **Réseau** — bridges, bonds, interfaces, adresses |
| `node firewall` | **Règles pare-feu** du nœud |
| `node updates` | **Mises à jour disponibles** (APT) |
| `node backup --vmid <id> [--mode snapshot\|suspend\|stop]` | **Backup** d'une VM via vzdump |
| `node backups [--storage <nom>]` | **Liste des backups** disponibles |

**Options de backup :**
- `--mode snapshot\|suspend\|stop` — Mode de backup (défaut: `snapshot`)
- `--compress 0\|1\|lzo\|gzip\|zstd` — Algorithme de compression (défaut: `zstd`)

### Exemples

```bash
# État du cluster
python -m proxmox_cli.main list --type qemu --format json

# Infos détaillées du nœud
python -m proxmox_cli.main node info

# Stockage et utilisation
python -m proxmox_cli.main node storage

# Backup d'une VM
python -m proxmox_cli.main node backup --vmid 100 --mode snapshot

# Lister les backups
python -m proxmox_cli.main node backups --storage local

# Voir les tâches récentes
python -m proxmox_cli.main node tasks --limit 10

# Cloner un template
python -m proxmox_cli.main clone --source-id 9000 --new-id 100 --name "web-server" --node "pve1" --full
```

## Skill IA

Le fichier `SKILL.md` fournit les instructions pour qu'un agent IA pilote cet outil de manière idempotente.
Le fichier `AGENTS.md` documente l'intégration GitNexus et les conventions de développement.
