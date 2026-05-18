# hermes-proxmox-cli

CLI de pilotage d'infrastructure Proxmox conçu pour être utilisé par des humains et des agents IA (Hermes Agent, Claude Code, Qwen, Antigravity).

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

## Utilisation

Toutes les commandes supportent `--format json` pour l'intégration IA.

```bash
# Lister les ressources
python -m proxmox_cli.main list

# Cloner une VM/Template
python -m proxmox_cli.main clone --source-id 100 --new-id 200 --name "my-new-vm" --node "pve1"

# Configurer Cloud-Init
python -m proxmox_cli.main config --vmid 200 --node "pve1" --memory 2048 --ip "192.168.1.50/24" --gw "192.168.1.1"

# Gérer le cycle de vie
python -m proxmox_cli.main manage start --vmid 200 --node "pve1"
python -m proxmox_cli.main manage stop --vmid 200 --node "pve1"
python -m proxmox_cli.main manage delete --vmid 200 --node "pve1"
```

## Skill IA

Le fichier `SKILL.md` à la racine fournit les instructions pour qu'un agent IA pilote cet outil de manière idempotente.
