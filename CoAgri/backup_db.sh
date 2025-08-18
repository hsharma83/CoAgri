#!/bin/bash

# PostgreSQL Backup Script for CoAgri

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Variables
BACKUP_DIR="/var/backups/coagri"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/coagri_backup_$DATE.sql"
DAYS_TO_KEEP=7

# Create backup directory
sudo mkdir -p $BACKUP_DIR

# Create backup
echo "Creating PostgreSQL backup..."
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

echo "Backup created: ${BACKUP_FILE}.gz"

# Remove old backups
find $BACKUP_DIR -name "coagri_backup_*.sql.gz" -mtime +$DAYS_TO_KEEP -delete

echo "Backup completed successfully!"
echo "Backup location: ${BACKUP_FILE}.gz"