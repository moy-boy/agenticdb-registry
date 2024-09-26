#!/bin/bash

# CLEAN ALL COLLECTIONS (DB)

# Default URL if not provided
url="http://127.0.0.1:8000/collections"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --url) url="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

curl -X DELETE "$url"

