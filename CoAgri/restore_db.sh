#!/bin/bash

# PostgreSQL Restore Script for CoAgri

set -e

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo "Available backups:"
    ls -la /var/backups/coagri/coagri_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file '$BACKUP_FILE' not found!"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "Restoring database from: $BACKUP_FILE"
echo "This will overwrite the current database. Are you sure? (y/N)"
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 0
fi

# Create temporary file for decompressed backup
TEMP_FILE="/tmp/coagri_restore_$(date +%s).sql"

# Decompress backup
echo "Decompressing backup..."
gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"

# Drop and recreate database
echo "Recreating database..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# Restore database
echo "Restoring data..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TEMP_FILE"

# Clean up
rm "$TEMP_FILE"

echo "Database restore completed successfully!"
echo "Don't forget to run: python manage.py migrate"