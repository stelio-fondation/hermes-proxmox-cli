# hermes-proxmox-cli

[![CI](https://github.com/stelio-fondation/hermes-proxmox-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/stelio-fondation/hermes-proxmox-cli/actions)

CLI de pilotage d'infrastructure Proxmox — gestion des VMs/CTs et administration du nœud hyperviseur.
Conçu pour les humains et les agents IA (Hermes Agent, Claude Code, etc.).

## Installation

```bash
uv sync
```

## Configuration

```bash
export PM_URL="https://your-proxmox-ip:8006/api2/json"
export PM_USER="root@pam!mytokenid"
export PM_TOKEN="your-token"
export PM_VERIFY_SSL="false"
```

## Commandes

Toutes les commandes supportent `--format json` (ou `text` par défaut) pour l'intégration IA.

### Gestion des VMs / CTs

| Commande | Description |
|---|---|
| `list [--type qemu|lxc] [--sort vmid|name|cpu|mem] [--filter key=val] [--details]` | Lister les ressources avec filtres et tri avancés |
| `clone --source-id --new-id --name --node [--target-node]` | Cloner une VM/template |
| `config --vmid --node [--memory] [--cores] [--ip] [--gw] [--ssh-key] [--net] [--disk] [--ostype] ...` | Configurer une VM (mémoire, CPU, Cloud-Init, réseau, disque, OS) |
| `manage start --vmid --node` | Démarrer une VM/CT |
| `manage stop --vmid --node [--force] [--wait]` | Arrêter une VM/CT (shutdown gracieux par défaut) |
| `manage delete --vmid --node` | Supprimer une VM/CT |

### Snapshots

| Commande | Description |
|---|---|
| `snapshot list --vmid --node` | Lister les snapshots |
| `snapshot create --vmid --node --name [--description]` | Créer un snapshot |
| `snapshot rollback --vmid --node --name` | Restaurer un snapshot |
| `snapshot delete --vmid --node --name [--force]` | Supprimer un snapshot |

### Templates

| Commande | Description |
|---|---|
| `template list [--node] [--type]` | Lister les templates disponibles |
| `template deploy --source-id --new-id --name --node [--memory] [--cores] [--storage]` | Déployer depuis un template |
| `template convert --vmid --node [--force]` | Convertir une VM en template |

### Administration du nœud

| Commande | Description |
|---|---|
| `node status` | État global du nœud — uptime, CPU, RAM, load, version PVE |
| `node info` | Infos système détaillées — kernel, modèle CPU, swap |
| `node storage` | Liste des stockages avec utilisation |
| `node backup --vmid` | Lancer un backup |
| `node backups` | Lister les backups |
| `node services` | État des services PVE |
| `node tasks [--limit]` | Dernières tâches |
| `node network` | Configuration réseau |
| `node updates` | Mises à jour disponibles |
| `node firewall` | Règles du firewall |

## Développement

```bash
# Lancer les tests
uv run pytest tests/ -v

# Avec couverture
uv run pytest tests/ -v --cov=proxmox_cli --cov-report=term-missing

# Linting
uv run ruff check proxmox_cli/ tests/
```
