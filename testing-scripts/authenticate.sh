#!/bin/sh
curl -i -XPOST \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'grant_type=client_credentials&client_id=[YOUR CLIENT CREDENTIALS]&client_secret=[YOUR CLIENT SECRET]&scope=alexa::devices:all:notifications:write' https://api.amazon.com/auth/o2/token
