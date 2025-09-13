#!/bin/bash

# Forzar el uso de Node.js v20
export PATH="/Users/julio/.nvm/versions/node/v20.18.1/bin:$PATH"

# Verificar que estamos usando la versión correcta
echo "Using Node.js version: $(node --version)" >&2

# Ejecutar mcp-remote con los parámetros correctos
exec npx mcp-remote@latest "$@"