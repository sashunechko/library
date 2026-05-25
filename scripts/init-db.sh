#!/bin/bash
# Скрипт инициализации Postgres — выполняется один раз при создании volume.
# Заводит тестовую БД, чтобы pytest имел куда коннектиться.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE library_test;
EOSQL
