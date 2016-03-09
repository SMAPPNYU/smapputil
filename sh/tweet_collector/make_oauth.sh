#!/bin/bash

#this shell script is used to automatically generate oauth files

#create the structure
struct="{
    \"consumer_key\": \"$2\",
    \"consumer_secret\": \"$3\",
    \"access_token\": \"$4\",
    \"access_token_secret\": \"$5\"
}"

touch ~/oauth/$1.oauth.json

#create the file
cat > ~/oauth/$1.oauth.json << EOF1
$struct
EOF1
