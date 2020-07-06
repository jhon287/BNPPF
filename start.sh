#!/bin/sh

echo "Current Version: $(python --version)"

/wait && "$@"
