#!/bin/bash
echo "Starting EMC Knowledge Graph Client..."
if command -v python3 &> /dev/null; then
    echo "Starting Python HTTP server on port 8080..."
    cd "$(dirname "$0")"
    python3 -m http.server 8080
elif command -v python &> /dev/null; then
    echo "Starting Python HTTP server on port 8080..."
    cd "$(dirname "$0")"
    python -m http.server 8080
else
    echo "Python not found. Opening file directly..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open emc_standalone_client.html
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open emc_standalone_client.html
    elif [[ "$OSTYPE" == "msys" ]]; then
        start emc_standalone_client.html
    fi
fi