#!/usr/bin/env bash
set -u

# Server AG low-risk cleanup quarantine mover.
# Default mode is dry-run. Run with --apply only after backup and review.

APPLY=0
PUBLIC_HTML="${PUBLIC_HTML:-$PWD}"
QUARANTINE="${QUARANTINE:-_archive_cleanup_$(date +%Y%m%d_%H%M%S)}"

if [ "${1:-}" = "--apply" ]; then
  APPLY=1
fi

ITEMS=(
  "error_log"
  ".index.html.swp"
  ".htaccess.181215165729.orig"
  ".htaccess.181215173804.orig"
  ".htaccess.2"
  ".htaccess.andabien"
  ".htaccess.disabled"
  ".htaccess.old"
  "wp-config-sample.php"
  "readme.html"
  "license.txt"
  "licencia.txt"
  "wp-content/plugins/woocommerce"
  "wp-content/plugins/woocommerce-admin"
  "wp-content/plugins/yith-woocommerce-ajax-navigation"
  "wp-content/plugins/yith-woocommerce-catalog-mode"
  "wp-content/plugins/updraftplus"
  "wp-content/plugins/autoptimize"
  "wp-content/plugins/resmushit-image-optimizer"
  "grupoag/wp-content/plugins/post-duplicator"
  "liggett/wp-content/plugins/w3-total-cache"
)

NEVER=(
  ".htaccess"
  ".user.ini"
  "php.ini"
  "web.config"
  "wp-config.php"
  "wp-admin"
  "wp-includes"
  "wp-content/themes/ag"
  "wp-content/uploads"
  "liggett"
  "grupoag"
  "prode"
)

cd "$PUBLIC_HTML" || {
  echo "Cannot cd to PUBLIC_HTML=$PUBLIC_HTML" >&2
  exit 2
}

case "$QUARANTINE" in
  ""|"/"|"."|".."|*"/.."*|*".."*"/"*)
    echo "Unsafe QUARANTINE=$QUARANTINE" >&2
    exit 3
    ;;
esac

for item in "${ITEMS[@]}"; do
  for protected in "${NEVER[@]}"; do
    if [ "$item" = "$protected" ]; then
      echo "Refusing protected path: $item" >&2
      exit 4
    fi
  done
done

if [ "$APPLY" -eq 1 ]; then
  echo "APPLY mode. Moving low-risk items into $QUARANTINE"
  mkdir -p "$QUARANTINE"
else
  echo "DRY-RUN mode. Nothing will be moved."
  echo "Target quarantine would be: $QUARANTINE"
fi

MOVED=0
SKIPPED=0
for item in "${ITEMS[@]}"; do
  if [ ! -e "$item" ]; then
    echo "SKIP missing: $item"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi
  target="$QUARANTINE/$item"
  echo "MOVE: $item -> $target"
  if [ "$APPLY" -eq 1 ]; then
    mkdir -p "$(dirname "$target")"
    mv -- "$item" "$target"
    MOVED=$((MOVED + 1))
  fi
done

echo "Done. moved=$MOVED skipped=$SKIPPED apply=$APPLY"
