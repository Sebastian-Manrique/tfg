#!/bin/bash

# Ir al directorio raíz del proyecto
cd "$(dirname "$0")"

# Ejecutar el módulo con PYTHONPATH apuntando a src/
PYTHONPATH=src python -m core.api.endpoints
