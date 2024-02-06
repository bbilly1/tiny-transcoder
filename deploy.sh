#!/bin/bash

set -e

function validate {

    if [[ $1 ]]; then
        check_path="$1"
    else
        check_path="."
    fi

    echo "run validate on $check_path"

    echo "running black"
    black --diff --color --check -l 79 "$check_path"
    echo "running codespell"
    codespell --skip="./.git,./.venv,./app/package.json,./app/package-lock.json,./app/node_modules,./.mypy_cache,./app/static/dist" "$check_path"
    echo "running flake8"
    flake8 "$check_path" --exclude ".venv" --count --max-complexity=10 \
        --max-line-length=79 --show-source --statistics
    echo "running isort"
    isort --skip ".venv" --check-only --diff --profile black -l 79 "$check_path"
    printf "    \n> all validations passed\n"

}

function sync_docker {

    # start build
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -t bbilly1/tiny-transcoder --push .

}

if [[ $1 == "validate" ]]; then
    validate "$2"
elif [[ $1 == "docker" ]]; then
    sync_docker
else
    echo "valid options are: validate"
fi


##
exit 0
