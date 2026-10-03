#!/usr/bin/env bash
set -euo pipefail

TARGET_URL="${1:-http://localhost:5000/info}"
REQUEST_COUNT="${2:-100}"

echo "=========================================================="
echo "Simulating Traffic to ${TARGET_URL}"
echo "Sending ${REQUEST_COUNT} requests..."
echo "============================================================"

SUCCESS=0
FAILED=0

for i in $(seq 1 "${REQUEST_COUNT}"); do
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${TARGET_URL}" || echo "000")
    if [[ "${STATUS_CODE}" =~ ^2 ]]; then
        SUCCESS=$((SUCCESS + 1))
        echo -n "."
    else
        FAILED=$((FAILED + 1))
        echo -n "x"
    fi
    if [ $((i % 50)) -eq 0 ]; then
        echo " [${i}/${REQUEST_COUNT}]"
    fi
    sleep 0.1
done

echo ""
echo "Traffic simulation complete: ${SUCCESS} successful, ${FAILED} failed."
echo "=========================================================="
