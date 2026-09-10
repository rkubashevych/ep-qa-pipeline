#!/usr/bin/env bash
# Safe .env value loader (api-testing reference §0) + the EP_QA_HOME
# resolution (qa-pipeline/references/environment.md). Handles quoted
# values and shell metacharacters in passwords. Never echo a value.
#
# Source it:            source load-env.sh
#                       ENVFILE=$(ep_qa_env_file) || exit 1
#                       ADMIN_PASSWORD=$(getenvvar ADMIN_PASSWORD "$ENVFILE")
#                       host_allowed api-alpha2.example.test "$ENVFILE" || exit 1
# Or run it directly:   ./load-env.sh ADMIN_PASSWORD            (file resolved)
#                       ./load-env.sh ADMIN_PASSWORD path/to/.env
#                       ./load-env.sh --home                    (prints EP_QA_HOME)
#                       ./load-env.sh --env-file                (prints the file path)
#                       ./load-env.sh --host-allowed HOST       (exit 0/1)

getenvvar() {  # getenvvar NAME FILE
  grep -m1 "^$1=" "$2" | cut -d= -f2- | sed "s/^'//; s/'\$//; s/^\"//; s/\"\$//"
}

ep_qa_home() {  # $EP_QA_HOME → ~/.ep-qa → (legacy, read-only) the plugin checkout
  if [[ -n "${EP_QA_HOME:-}" ]]; then printf '%s\n' "$EP_QA_HOME"; return 0; fi
  if [[ -d "$HOME/.ep-qa" ]]; then printf '%s\n' "$HOME/.ep-qa"; return 0; fi
  if [[ -n "${USERPROFILE:-}" && -d "$USERPROFILE/.ep-qa" ]]; then printf '%s\n' "$USERPROFILE/.ep-qa"; return 0; fi
  local here; here="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
  if [[ -f "$here/.env.qa-agents" || -d "$here/runs" ]]; then
    echo "load-env: legacy layout — $here holds .env.qa-agents/runs; move them to ~/.ep-qa (environment.md)" >&2
    printf '%s\n' "$here"; return 0
  fi
  echo "load-env: no EP_QA_HOME, no ~/.ep-qa — create it and put .env.qa-agents in it" >&2
  return 1
}

ep_qa_env_file() {  # the credentials file, or exit 1 with the reason on stderr
  local home; home="$(ep_qa_home)" || return 1
  if [[ -f "$home/.env.qa-agents" ]]; then printf '%s\n' "$home/.env.qa-agents"; return 0; fi
  echo "load-env: $home/.env.qa-agents not found" >&2
  return 1
}

host_allowed() {  # host_allowed HOST FILE → 0 when HOST matches ALLOWED_HOSTS; production always 1
  local host="${1,,}" file="$2" list entry entries
  case "$host" in *.expoplatform.com|expoplatform.com)
    echo "host_allowed: $host is production — refused regardless of the list" >&2; return 1;; esac
  list="$(getenvvar ALLOWED_HOSTS "$file")"
  if [[ -z "$list" ]]; then
    echo "host_allowed: ALLOWED_HOSTS is not set in $file — a run without a list does not start" >&2; return 1
  fi
  IFS=',' read -ra entries <<< "$list"
  for entry in "${entries[@]}"; do
    entry="$(printf '%s' "$entry" | tr -d ' ' | tr '[:upper:]' '[:lower:]')"
    [[ -z "$entry" ]] && continue
    if [[ "$entry" == \*.* ]]; then
      [[ "$host" == *".${entry#\*.}" ]] && return 0
    else
      [[ "$host" == "$entry" ]] && return 0
    fi
  done
  echo "host_allowed: $host is not in ALLOWED_HOSTS ($list) — add it or name another host" >&2
  return 1
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  case "${1:-}" in
    --home) ep_qa_home ;;
    --env-file) ep_qa_env_file ;;
    --host-allowed) f="$(ep_qa_env_file)" || exit 1; host_allowed "$2" "$f" ;;
    "") echo "usage: load-env.sh NAME [FILE] | --home | --env-file | --host-allowed HOST" >&2; exit 1 ;;
    *) f="${2:-}"; [[ -n "$f" ]] || f="$(ep_qa_env_file)" || exit 1; getenvvar "$1" "$f" ;;
  esac
fi
