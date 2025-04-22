#!/bin/sh
URL="http://localhost:7200/rest/repositories/"
STATUS_CODE=$(wget --server-response --spider "$URL" 2>&1 \
    | awk '/HTTP\// {print $2}' | head -n1)
echo "STATUS_CODE : $STATUS_CODE"
if [ "$STATUS_CODE" = "200" ] || [ "$STATUS_CODE" = "401" ]; then
    exit 0
fi
exit 1