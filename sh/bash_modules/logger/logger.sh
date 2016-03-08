#!/bin/bash

declare logpath=''

# logs output to sh
log () { echo "$1" >> "$logpath"; }

# sets the name of the current running script
setlogpath () { logpath="$1"; }

# c* https://stackoverflow.com/questions/6366530/bash-syntax-error-unexpected-end-of-file/24636016#24636016