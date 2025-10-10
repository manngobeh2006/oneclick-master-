#!/bin/bash

# OneClick Master AWS Deployment Script

echo "🎵 Deploying OneClick Master to AWS..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Installing..."
    curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
    sudo installer -pkg AWSCLIV2.pkg -target /
fi

# Create S3 bucket for static assets
BUCKET_NAME="oneclick-master-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Build frontend
echo "🔨 Building frontend..."
cd frontend
npm install --production
npm run build
cd ..

# Upload frontend to S3
echo "📤 Uploading frontend to S3..."
aws s3 sync frontend/dist/ s3://$BUCKET_NAME --delete --region us-east-1

# Create App Runner service
echo "🚀 Creating App Runner service..."
aws apprunner create-service \
    --service-name "oneclick-master" \
    --source-configuration '{
        "GitRepository": {
            "repositoryUrl": "https://github.com/manngobeh2006/oneclick-master-.git",
            "sourceCodeVersion": {
                "type": "BRANCH",
                "value": "main"
            },
            "configurationSource": "REPOSITORY"
        },
        "autoDeploymentsEnabled": true
    }' \
    --instance-configuration '{
        "cpu": "1 vCPU",
        "memory": "2 GB"
    }' \
    --region us-east-1

echo "✅ Deployment started! Check AWS App Runner console for status."
echo "🔗 Frontend URL: http://$BUCKET_NAME.s3-website-us-east-1.amazonaws.com"