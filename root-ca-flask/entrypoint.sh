#!/bin/sh
set -e
mkdir -p "$DATA_PATH/issued"
if [ ! -f "$DATA_PATH/root_cert.pem" ]; then
  echo "=== Initializing Root CA ==="
  python - <<'PYCODE'
import crypto_utils
crypto_utils.generate_root()
PYCODE
  echo "=== Root CA created ==="
fi
exec "$@"
