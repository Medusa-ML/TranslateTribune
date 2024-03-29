#!/bin/bash

docker volume rm tt-logs 
#remove the `-it` flag and add `-d` if you are running via a timer/cron job
docker run --rm -it -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY -e OPENAI_API_KEY=$OPENAI_API_KEY -e MISTRAL_API_KEY=$MISTRAL_API_KEY -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e NOTDIAMOND_API_KEY=$NOTDIAMOND_API_KEY -e DEBUG=true -v $(pwd)/debug:/usr/src/app/debug -v tt-logs:/var/log/tt --ulimit nofile=32768 ghcr.io/medusa-ml/translatetribune:latest

