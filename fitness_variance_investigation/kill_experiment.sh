#!/bin/bash

# Replace this with the name of your script
SCRIPT_NAME="run.sh"

# Find the PID of the script
PARENT_PID=$(ps -ef | grep "$SCRIPT_NAME" | grep -v grep | awk '{print $2}')

# Kill the parent process and its children
if [ ! -z "$PARENT_PID" ]; then
    pkill -TERM -P $PARENT_PID
    kill -TERM $PARENT_PID
fi

# Note: use htop to see resource usage
