# AWS DynamoDB Setup Guide

Quick setup guide for DynamoDB tables and AWS credentials.

## 1. AWS Account Setup

1. **Create AWS Account** (if you don't have one)

   - Go to https://aws.amazon.com/
   - Sign up for free tier (includes DynamoDB free tier)

2. **Create IAM User** (recommended for security)
   - Go to AWS Console → IAM → Users → Create User
   - User name: `vthacks-backend-user`
   - Attach policy: `AmazonDynamoDBFullAccess`
   - Create access key for programmatic access

## 2. DynamoDB Tables Creation

### Option A: Automatic Creation (Recommended for Development)

The application will automatically create tables when it starts. Just provide AWS credentials in `.env`:

```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
```

### Option B: Manual Creation (AWS Console)

1. **Users Table:**

   ```
   Table Name: vthacks25-users
   Partition Key: userId (String)
   Global Secondary Index:
     - Index Name: username-index
     - Partition Key: username (String)
   Billing Mode: Pay-per-request
   ```

## 3. Cost Estimation

### Free Tier (First 12 months):

- **Storage**: 25 GB free
- **Read/Write**: 25 read + 25 write capacity units
- **Estimated usage**: FREE for typical hackathon + early development

### Pay-per-request pricing (after free tier):

- **Reads**: $0.25 per million requests
- **Writes**: $1.25 per million requests
- **Storage**: $0.25 per GB per month

**Realistic monthly cost for small app**: $0-5/month

## 4. Environment Configuration

Update your `.env` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# DynamoDB Table (optional - default provided)
DYNAMODB_USERS_TABLE=vthacks25-users
```

## 5. Testing the Setup

```bash
# Test user authentication
python test_user_auth.py

# Test video processing with user context
python test_video_upload.py sample_video.mp4
```

## 6. Production Deployment Considerations

- **Security**: Use IAM roles instead of access keys for Lambda
- **Monitoring**: Enable CloudWatch for DynamoDB
- **Backup**: Enable point-in-time recovery
- **Scaling**: DynamoDB auto-scales with pay-per-request

## 7. Migration from SQLite (if needed)

If you started with SQLite and want to migrate:

```python
# Migration script (create if needed)
def migrate_sqlite_to_dynamodb():
    # 1. Export SQLite data
    # 2. Transform to DynamoDB format
    # 3. Batch write to DynamoDB
    pass
```

## Troubleshooting

### Common Issues:

1. **"Unable to locate credentials"**

   - Check `.env` file has correct AWS keys
   - Verify keys are not quoted

2. **"Table already exists"**

   - Normal message, tables exist from previous run

3. **"Access denied"**
   - Verify IAM user has DynamoDB permissions
   - Check AWS region matches your account

### Local Development Alternative

For pure local development without AWS:

- Use DynamoDB Local: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html
- Or switch back to SQLite by changing database imports

## Next Steps

Once DynamoDB is working:

1. ✅ User signup/signin works
2. ✅ Preferences are stored in DynamoDB
3. ✅ Video processing integrates with user context
4. 🚀 Deploy to AWS Lambda with zero database migration needed!
