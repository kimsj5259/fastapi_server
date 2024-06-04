#!/bin/bash
DEPLOYMENT=$1

case $DEPLOYMENT in
development ) AWS_SECRET_ID_TOP="dev/backend/jin" ;;
staging ) AWS_SECRET_ID_TOP="staging/backend/jin" ;;
production ) AWS_SECRET_ID_TOP="prod/backend/jin" ;;
* ) AWS_SECRET_ID_TOP="dev/backend/jin" ;;
esac

AWS_REGION="ap-northeast-2"
ENVFILE_TOP="./.env"

cd /home/ubuntu/jin/fastapi-deploy
echo "Fetch $ENVFILE_TOP"
aws secretsmanager get-secret-value --secret-id $AWS_SECRET_ID_TOP --region $AWS_REGION | jq -r '.SecretString' > $ENVFILE_TOP
