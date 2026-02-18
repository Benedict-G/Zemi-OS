#!/bin/bash

# Zemi Encrypted Backup Script
# Creates encrypted tarball of critical data

BACKUP_DIR="/Users/zemi/ZemiV1/backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="zemi_backup_${DATE}.tar.gz"
ENCRYPTED_FILE="${BACKUP_FILE}.enc"

echo "=== Zemi Backup Starting at $(date) ==="

# Create backup tarball
echo "Creating backup archive..."
cd /Users/zemi/ZemiV1

tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    vault/ \
    memory/ \
    logs/ \
    core/*.py \
    docs/ \
    docker/matrix_data/ \
    --exclude='*.pyc' \
    --exclude='__pycache__'

echo "✓ Archive created: ${BACKUP_FILE}"

# Encrypt with openssl
echo "Encrypting backup..."
openssl enc -aes-256-cbc -salt -pbkdf2 \
    -in "${BACKUP_DIR}/${BACKUP_FILE}" \
    -out "${BACKUP_DIR}/${ENCRYPTED_FILE}" \
    -pass file:vault/master.key

# Remove unencrypted archive
rm "${BACKUP_DIR}/${BACKUP_FILE}"

echo "✓ Encrypted backup: ${ENCRYPTED_FILE}"

# Keep only last 7 backups
echo "Cleaning old backups..."
cd "${BACKUP_DIR}"
ls -t zemi_backup_*.tar.gz.enc | tail -n +8 | xargs rm -f 2>/dev/null

echo "✓ Backup complete!"
echo "Location: ${BACKUP_DIR}/${ENCRYPTED_FILE}"
