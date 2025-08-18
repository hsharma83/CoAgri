#!/bin/bash

# CoAgri Django Deployment Script for Ubuntu VPS

set -e

echo "Starting CoAgri deployment..."

# Variables
PROJECT_NAME="coagri"
PROJECT_DIR="/var/www/$PROJECT_NAME"
REPO_URL="https://github.com/hsharma83/coagri.git"  # Update this
PYTHON_VERSION="3.11"
VENV_DIR="$PROJECT_DIR/venv"

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor git openssl

# Create project directory
echo "Setting up project directory..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Clone repository
echo "Cloning repository..."
if [ -d "$PROJECT_DIR/.git" ]; then
    cd $PROJECT_DIR
    git pull origin main
else
    git clone $REPO_URL $PROJECT_DIR
    cd $PROJECT_DIR
fi

# Navigate to Django project
cd CoAgri/CoAgri

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup PostgreSQL database
echo "Setting up PostgreSQL database..."
chmod +x setup_postgresql.sh
./setup_postgresql.sh

# Create necessary directories
sudo mkdir -p /var/log/gunicorn
sudo mkdir -p /var/www/$PROJECT_NAME/static
sudo mkdir -p /var/www/$PROJECT_NAME/media
sudo chown -R www-data:www-data /var/log/gunicorn
sudo chown -R www-data:www-data /var/www/$PROJECT_NAME

# Django setup
echo "Running Django migrations..."
python manage.py collectstatic --noinput
python manage.py migrate

echo "Deployment script completed!"
echo "Next steps:"
echo "1. Configure Nginx"
echo "2. Setup Supervisor for Gunicorn"
echo "3. Generate new SECRET_KEY for production"
echo "4. Create Django superuser: python manage.py createsuperuser"