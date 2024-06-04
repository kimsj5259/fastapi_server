#!/bin/bash

source ~/.profile

cd /home/ubuntu/jin/fastapi-deploy

sh scripts/fetch_env.sh ${DEPLOY_ENV}

if [ $DEPLOY_ENV = "production" ]; then
    echo "prod 환경"
    sudo make run-prod-build
else
    echo "dev 환경"
    sudo make run-dev-aws-build
fi
