# Zemi Backup & Restore Guide

## Backup Location
Encrypted backups: `~/ZemiV1/backups/`

## How to Restore a Backup

### 1. Decrypt the backup:
```bash
cd ~/ZemiV1
openssl enc -aes-256-cbc -d -pbkdf2 \
  -in backups/zemi_backup_YYYY-MM-DD_HH-MM-SS.tar.gz.enc \
  -out restore.tar.gz \
  -pass file:vault/master.key
```

### 2. Extract the files:
```bash
tar -xzf restore.tar.gz
```

### 3. Restart Zemi:
```bash
cd ~/ZemiV1/core
source ../venv/bin/activate
python zemi_main.py
```

## Backup Schedule
- **Automatic:** Weekly on Sundays at 2 AM
- **Manual:** Run `./backup_zemi.sh` anytime

## What's Backed Up
- ✅ Encrypted vault (credentials)
- ✅ Memory database
- ✅ All logs
- ✅ Python code (orchestrator, etc.)
- ✅ Documentation
- ✅ Matrix data

## What's NOT Backed Up
- Docker images (re-download if needed)
- Python venv (recreate with `python3 -m venv venv`)
- Ollama models (re-download if needed)
