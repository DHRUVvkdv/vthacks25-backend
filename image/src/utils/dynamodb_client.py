import boto3
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
import uuid

class DynamoDBClient:
    def __init__(self):
        # Initialize DynamoDB client
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Table name
        self.users_table_name = os.getenv('DYNAMODB_USERS_TABLE', 'vthacks25-users')
        
        # Get table reference
        self.users_table = self.dynamodb.Table(self.users_table_name)
    
    def create_table_if_not_exist(self):
        """Create DynamoDB users table if it doesn't exist (for local development)."""
        try:
            # Create Users table only
            self.users_table = self.dynamodb.create_table(
                TableName=self.users_table_name,
                KeySchema=[
                    {
                        'AttributeName': 'userId',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'userId',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'username',
                        'AttributeType': 'S'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'username-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'username',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            print(f"Created DynamoDB table: {self.users_table_name}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                # Table already exists
                print(f"DynamoDB table {self.users_table_name} already exists")
            else:
                print(f"Error creating table: {e}")
    
    # ============= USER OPERATIONS =============
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user in DynamoDB."""
        user_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'userId': user_id,
            'username': user_data['username'],
            'name': user_data['name'],
            'passwordHash': user_data['password_hash'],
            'preferences': {
                'age': user_data['age'],
                'academicLevel': user_data['academic_level'],
                'major': user_data['major'],
                'dyslexiaSupport': user_data.get('dyslexia_support', False),
                'languagePreference': user_data.get('language_preference', 'English'),
                'learningStyles': user_data.get('learning_styles', []),
                'metadata': user_data.get('metadata', [])
            },
            'createdAt': timestamp,
            'updatedAt': timestamp
        }
        
        try:
            self.users_table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(userId)'
            )
            return item
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username using GSI."""
        try:
            response = self.users_table.query(
                IndexName='username-index',
                KeyConditionExpression='username = :username',
                ExpressionAttributeValues={':username': username}
            )
            
            items = response.get('Items', [])
            return items[0] if items else None
            
        except ClientError as e:
            print(f"Error querying user by username: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by user ID."""
        try:
            response = self.users_table.get_item(
                Key={'userId': user_id}
            )
            return response.get('Item')
            
        except ClientError as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences."""
        try:
            # Build update expression with reserved keyword handling
            update_expression = "SET updatedAt = :timestamp"
            expression_values = {':timestamp': datetime.utcnow().isoformat()}
            expression_names = {}
            
            for key, value in preferences.items():
                if key == 'name':
                    # Handle 'name' as top-level field (reserved keyword)
                    expression_names['#n'] = 'name'
                    update_expression += f", #n = :{key}"
                    expression_values[f':{key}'] = value
                else:
                    # All other fields (including age) go into preferences
                    update_expression += f", preferences.{key} = :{key}"
                    expression_values[f':{key}'] = value
            
            update_params = {
                'Key': {'userId': user_id},
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_values,
                'ReturnValues': 'ALL_NEW'
            }
            
            # Add expression attribute names if we have any
            if expression_names:
                update_params['ExpressionAttributeNames'] = expression_names
            
            response = self.users_table.update_item(**update_params)
            
            return response['Attributes']
            
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user: {str(e)}"
            )
    
