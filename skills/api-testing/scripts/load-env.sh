#!/usr/bin/env bash
# Safe .env value loader (api-testing reference §0). Handles quoted
# values and shell metacharacters in passwords. Never echo the result.
#
# Source it:            source load-env.sh
#                       ADMIN_PASSWORD=$(getenvvar ADMIN_PASSWORD .env)
# Or run it directly:   ./load-env.sh ADMIN_PASSWORD path/to/.env
getenvvar() {  # getenvvar NAME FILE
  grep -m1 "^$1=" "$2" | cut -d= -f2- | sed "s/^'//; s/'\$//; s/^\"//; s/\"\$//"
}
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  [[ $# -ge 2 ]] || { echo "usage: load-env.sh NAME FILE" >&2; exit 1; }
  getenvvar "$1" "$2"
fi
