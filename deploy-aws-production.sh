#!/bin/bash

# AWS Deployment Script for OneClick Master
# Deploys to one-clickmaster.com domain

set -e

echo "🚀 Deploying OneClick Master to AWS..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS CLI not configured. Run 'aws configure' first."
    exit 1
fi

# Set variables
DOMAIN="one-clickmaster.com"
API_DOMAIN="api.one-clickmaster.com"
APP_NAME="oneclick-master-prod"
REGION="us-east-1"

echo "📋 Deployment Configuration:"
echo "  Domain: $DOMAIN"
echo "  API Domain: $API_DOMAIN"
echo "  Region: $REGION"
echo "  App Name: $APP_NAME"

# Create S3 bucket for frontend
echo "📦 Creating S3 bucket for frontend..."
aws s3 mb s3://$DOMAIN --region $REGION || echo "Bucket may already exist"

# Create S3 bucket for file uploads/outputs
echo "📦 Creating S3 buckets for file storage..."
aws s3 mb s3://$DOMAIN-uploads --region $REGION || echo "Bucket may already exist"
aws s3 mb s3://$DOMAIN-outputs --region $REGION || echo "Bucket may already exist"

# Build frontend with production API URL
echo "🏗️ Building frontend..."
cd frontend
VITE_API_URL=https://$API_DOMAIN npm run build

# Upload frontend to S3
echo "📤 Uploading frontend to S3..."
aws s3 sync dist/ s3://$DOMAIN --delete

# Configure S3 bucket for static website hosting
echo "🌐 Configuring S3 for static website hosting..."
aws s3 website s3://$DOMAIN --index-document index.html --error-document index.html

# Set S3 bucket policy for public read
cat > ../bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$DOMAIN/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $DOMAIN --policy file://../bucket-policy.json
rm ../bucket-policy.json

cd ..

# Deploy backend using App Runner
echo "🚀 Deploying backend to App Runner..."
echo "  You'll need to:"
echo "  1. Go to AWS App Runner console"
echo "  2. Create service from source code"
echo "  3. Connect your GitHub repository"
echo "  4. Use apprunner.yaml configuration"
echo "  5. Set custom domain: $API_DOMAIN"

# Create Route 53 hosted zone if it doesn't exist
echo "🌐 Setting up Route 53..."
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones-by-name --dns-name $DOMAIN --query 'HostedZones[0].Id' --output text 2>/dev/null || echo "None")

if [ "$HOSTED_ZONE_ID" = "None" ] || [ "$HOSTED_ZONE_ID" = "null" ]; then
    echo "Creating hosted zone for $DOMAIN..."
    aws route53 create-hosted-zone --name $DOMAIN --caller-reference $(date +%s)
    echo "⚠️ Update your domain's nameservers to point to Route 53"
fi

echo "✅ Frontend deployed to: http://$DOMAIN.s3-website-$REGION.amazonaws.com"
echo "📋 Next steps:"
echo "  1. Deploy backend via App Runner console"
echo "  2. Set up Route 53 A records:"
echo "     - $DOMAIN → S3 website endpoint"
echo "     - $API_DOMAIN → App Runner service"
echo "  3. Configure SSL certificates in CloudFront (optional)"
echo "  4. Set environment variables in App Runner:"
echo "     - STRIPE_PUBLIC_KEY"
echo "     - STRIPE_SECRET_KEY"
echo "     - STRIPE_PRICE_ID_SINGLE"
echo "     - STRIPE_PRICE_ID_SUB_MONTHLY"
echo "     - AWS_REGION=$REGION"
echo "     - S3_BUCKET_UPLOADS=$DOMAIN-uploads"
echo "     - S3_BUCKET_OUTPUTS=$DOMAIN-outputs"