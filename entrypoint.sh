#!/bin/sh
set -e

echo "Esperando a que MySQL esté listo..."
until nc -z db 3306; do
  sleep 1
done
echo "MySQL disponible."

# Corre migraciones pendientes en cada arranque del contenedor.
# Si migrations/ no existe todavía (primer deploy), hay que inicializarla
# manualmente antes — ver instrucciones abajo. Este script asume que
# migrations/ ya está commiteada en el repo.
flask db upgrade

exec "$@"