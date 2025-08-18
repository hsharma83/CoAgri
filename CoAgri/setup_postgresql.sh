#!/bin/bash

# PostgreSQL Setup Script for CoAgri Django Project

set -e

echo "Setting up PostgreSQL for CoAgri..."

# Variables
DB_NAME="coagri_db"
DB_USER="coagri_user"
DB_PASSWORD=""

# Function to generate random password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Installing PostgreSQL..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
else
    echo "PostgreSQL is already installed."
fi

# Generate secure password if not provided
if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(generate_password)
    echo "Generated secure password for database user."
fi

# Create database and user
echo "Creating database and user..."
sudo -u postgres psql << EOF
-- Create database
CREATE DATABASE $DB_NAME;

-- Create user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Grant privileges
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Grant schema privileges
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

\q
EOF

# Update .env file
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.example $ENV_FILE
    echo "Created .env file from template."
fi

# Update database configuration in .env
sed -i "s/DB_NAME=.*/DB_NAME=$DB_NAME/" $ENV_FILE
sed -i "s/DB_USER=.*/DB_USER=$DB_USER/" $ENV_FILE
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" $ENV_FILE

echo ""
echo "PostgreSQL setup completed successfully!"
echo ""
echo "Database Details:"
echo "  Database Name: $DB_NAME"
echo "  Username: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "Configuration has been updated in .env file."
echo ""
echo "Next steps:"
echo "1. Run: python manage.py migrate"
echo "2. Run: python manage.py createsuperuser"
echo ""
echo "To connect to the database manually:"
echo "  psql -h localhost -U $DB_USER -d $DB_NAME"