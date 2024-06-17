# Github Actions AWS Approval Lambda

This AWS Lambda function handles deployment approval requests from Slack. It processes approval or rejection actions for deployments and updates the Slack message accordingly. The function also manages authorized users for approval actions using a YAML configuration file.

## Features

- Processes deployment approval or rejection actions from Slack.
- Updates Slack messages with the current approval status.
- Ensures only authorized users can approve or reject deployments.
- Uses DynamoDB for storing approval statuses and details.
- Uses Redis for Pub/Sub.

## Deployment

**Install Dependencies**:
   
```
pip install -r requirements.txt -t ./packages
```

**Package Artifact**
```
cd packages && zip -r ../deployment.zip . && cd ..
zip deployment.zip lambda_function.py
zip -r deployment.zip core
zip deployment.zip approvers.yaml
```

**Deploy the Lambda Function**

- Create a DynamoDB table named `deployment_approvals`
- Create a ElastiCache instance (serverless is good) 
- Upload the `deployment.zip` artifact to AWS Lambda. Configure the following environment variables for the Lambda function:

```
REDIS_HOST
REDIS_PORT
SLACK_TOKEN
```

- Create an API Gateway that will trigger the function
- Set the request URL in your Slack App to use the API Gateway

See (https://github.com/jcputter/slack-approval-github-actions) for setting up the Github Action