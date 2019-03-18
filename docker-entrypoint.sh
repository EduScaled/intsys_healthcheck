#!/bin/bash
# by Evgeniy Bondarenko <Bondarenko.Hub@gmail.com>

# DynIP
IP=$(cat /etc/hosts|grep $HOSTNAME |awk '{print $1}')
echo "IP $IP"

export DB_HOST=${DB_HOST:-"localhost"}
export DB_PORT=${DB_PORT:-"5432"}
export DB_NAME=${DB_NAME:-"intsys"}
export DB_USER=${DB_USER:-"intsys"}
export DB_PASSWORD=${DB_PASSWORD:-"intsys"}
export SENTRY_DSN=${SENTRY_DSN:-"https://ec33c4a0117b4faea012fd7422ebcee3:7b69d46d2e834a5d8c4a646d9837bba1@sentry-bifok7.2035.university/19"}
export SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT:-intsys-health-check-stage}"

echo starting

exec "$@"