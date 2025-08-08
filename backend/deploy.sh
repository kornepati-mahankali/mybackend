#!/bin/bash

echo "🚀 Starting deployment to AWS Elastic Beanstalk..."

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Create deployment package
echo "📦 Creating deployment package..."

# Remove old deployment package if it exists
if [ -f "deployment.zip" ]; then
    rm deployment.zip
fi

# Create new deployment package
zip -r deployment.zip . -x "*.git*" "*.pyc" "__pycache__/*" "*.log" "deployment.zip" "test_db_connection.py"

echo "✅ Deployment package created: deployment.zip"

# Check package size
PACKAGE_SIZE=$(du -h deployment.zip | cut -f1)
echo "📊 Package size: $PACKAGE_SIZE"

# List contents of the package
echo "📋 Package contents:"
unzip -l deployment.zip | head -20

echo ""
echo "🎯 Next steps:"
echo "1. Upload deployment.zip to AWS Elastic Beanstalk"
echo "2. Or use: eb deploy (if you have EB CLI configured)"
echo "3. Monitor the deployment in the AWS Console"
echo ""
echo "🔍 To monitor deployment:"
echo "   - Check /var/log/eb-engine.log on the EC2 instance"
echo "   - Check /var/log/cfn-init.log for configuration errors"
echo "   - Use: eb logs (if you have EB CLI)"
echo ""
echo "✅ Deployment package ready!" 