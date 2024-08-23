#!/bin/sh
curl -H 'Content-Type: application/json' \
    -H 'Authorization: [YOUR AUTHENTICATION TOKEN]'\
    -X PUT "https://api.amazonalexa.com/v1/skills/[YOUR SKILL ID]/stages/development/enablement"
