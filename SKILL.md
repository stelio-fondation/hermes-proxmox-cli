---
name: proxmox-master
description: "Orchestration d'infrastructure Proxmox via proxmox-cli. Gestion idempotente des VMs."
risk: safe
source: local
date_added: "2026-04-11"
---

# Proxmox Master Orchestrator

## Purpose
Ce skill permet à un agent IA de piloter un cluster Proxmox de manière **déterministe** et **idempotente** à l'aide de l'outil `proxmox-cli`.

## Principes de Portabilité
Le skill est conçu pour fonctionner avec tout agent capable d'exécuter des commandes shell (Claude Code, Qwen, Antigravity, OpenCode).
L'agent doit avoir accès aux variables d'environnement suivantes :
- `PM_URL`
- `PM_USER`
- `PM_TOKEN`

## Workflow Idempotent (Strict)
Pour toute demande de modification de l'infrastructure, l'agent DOIT suivre ce cycle :

### 🔍 1. Discovery & State Check
Toujours commencer par lister l'état actuel :
```bash
python -m proxmox_cli.main --format json list
```
Analyser le JSON pour vérifier si la VM cible existe déjà par son nom ou son VMID.

### 🏗️ 2. Decision Logic
- **Si la VM n'existe pas** : Proceder au clonage (`clone`).
- **Si la VM existe mais l'état diffère** : Appliquer la configuration (`config`).
- **Si la VM est dans l'état souhaité** : Ne rien faire.

### 🛠️ 3. Execution
Commandes disponibles :
- **List** : `python -m proxmox_cli.main list [--node <name>] [--type qemu|lxc]`
- **Clone** : `python -m proxmox_cli.main clone --source-id <id> --new-id <id> --name <name> --node <node>`
- **Config** : `python -m proxmox_cli.main config --vmid <id> --node <node> [--memory <MB>] [--cores <N>] [--ip <CIDR>] [--gw <IP>]`
- **Manage** : `python -m proxmox_cli.main manage [start|stop|delete] --vmid <id> --node <node>`

### 🖥️ 4. Node Management (local hypervisor)

État du nœud, stockage, services, réseau, backups et tâches :

| Commande | Usage |
|---|---|
| `node status` | État global (uptime, CPU, RAM, load, version PVE) |
| `node info` | Infos détaillées (kernel, modèle CPU, swap, loads) |
| `node storage` | Stockages disponibles et occupation |
| `node services` | Statut des services PVE |
| `node tasks --limit N` | Historique des N dernières tâches |
| `node network` | Configuration réseau (bridges, bonds, adresses) |
| `node firewall` | Règles de pare-feu |
| `node updates` | Mises à jour APT disponibles |
| `node backup --vmid <id>` | Backup vzdump d'une VM (mode: snapshot/suspend/stop) |
| `node backups --storage <nom>` | Lister les backups sur un stockage |

## Best Practices
- Toujours utiliser `--format json` pour une lecture fiable des données.
- Privilégier le clonage à partir de templates pour assurer la reproductibilité.
- Utiliser Cloud-Init (`config --ip --ssh-key`) pour éviter les configurations manuelles post-déploiement.

---

## Exit Criteria
- L'infrastructure cible correspond exactement à la demande de l'utilisateur.
- Aucun doublon n'a été créé.
- Toutes les VMs sont dans l'état de puissance (start/stop) demandé.
