#!/bin/sh
# Configuración inicial (una sola vez) de la instancia EC2 Ubuntu Server.
# Uso, ya conectado por SSH:   sh setup_ec2.sh
set -e

echo ">> Instalando Docker Engine (script oficial de Docker)"
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl
curl -fsSL https://get.docker.com | sudo sh

echo ">> Permitiendo que el usuario $USER use docker sin sudo"
sudo usermod -aG docker "$USER"

echo ">> Habilitando Docker al arranque"
sudo systemctl enable --now docker

docker --version || true
echo ">> Listo. Cierra la sesión SSH y vuelve a entrar para que el grupo 'docker' surta efecto."
