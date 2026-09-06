#!/bin/bash

echo "Sending 7 rapid requests to test rate limiting (limit: 5/minute)..."
echo ""

for i in {1..7}; do
  status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
  echo "Request $i: $status"
  if [ "$status" == "429" ]; then
    echo "  --> Rate limit triggered as expected"
  fi
done
