import boto3
import os
from cachetools import Cache

# Configure AWS credentials
session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name='us-east-1'
)

# Create a Cognito client
client = session.client('cognito-idp', region_name='us-east-1')
user_pool_name = "ccgroup18"
user_pool_id = ""
app_client_name = "awsusecase"
app_client_id = ""

cache = Cache(maxsize=60)

# Create a user pool with disabled email and phone number verification
def create_user_pool(pool_name):
    try:
        
        response = client.create_user_pool(
            PoolName=pool_name,
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': True,
                    'RequireLowercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': True,
                    'TemporaryPasswordValidityDays': 7
                }
            },
            AutoVerifiedAttributes=[],
            MfaConfiguration='OFF',
            AccountRecoverySetting={
                'RecoveryMechanisms': [
                    {
                        'Priority': 1,
                        'Name': 'verified_email'
                    },
                    {
                        'Priority': 2,
                        'Name': 'verified_phone_number'
                    }
                ]
            }
        )
        print('User pool created successfully')
        user_pool_id = response['UserPool']['Id']
        response = client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=app_client_name,
            ExplicitAuthFlows=['USER_PASSWORD_AUTH'],
        )
        app_client_id = response['UserPoolClient']['ClientId']
        cache['user_pool_id'] = user_pool_id
        cache['app_client_id'] = app_client_id
        return user_pool_id, app_client_id
    except client.exceptions.ClientError as e:
        print('Error creating user pool:', e)
        return None, None

# Usage example
def check_user_pool_exists(user_pool_name):
    response = client.list_user_pools(MaxResults=60)  # Adjust MaxResults as per your requirements

    for user_pool in response['UserPools']:
        if user_pool['Name'] == user_pool_name:
            user_pool_id = user_pool['Id']
            
            # Get the app clients for the user pool
            response = client.list_user_pool_clients(
                UserPoolId=user_pool_id,
                MaxResults=60  # Adjust MaxResults as per your requirements
            )

            # Check if there are any app clients
            if response['UserPoolClients']:
                # Return the ID of the first app client
                app_client_id = response['UserPoolClients'][0]['ClientId']
                return True, user_pool_id, app_client_id

    return False, None, None

def create_user_pool_if_not_exists(user_pool_name):
    exists, user_pool_id, app_client_id = check_user_pool_exists(user_pool_name)
    if not exists:
        user_pool_id, app_client_id = create_user_pool(user_pool_name)
        return user_pool_id, app_client_id
    else:
        return user_pool_id, app_client_id


def create_user(username, password, email):
    user_pool_id, _ = create_user_pool_if_not_exists(user_pool_name)
    print("user_pool_id: ", user_pool_id)
    response = client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        TemporaryPassword=password,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email
            }
        ],
        MessageAction='SUPPRESS'  # Optional: Set to 'SUPPRESS' to not send a confirmation email
    )
    user_id = response['User']
    if user_id:
        print('User created successfully')
        print('User ID:', user_id)
        cache['user_id'] = user_id
        print('Setting permanent password as same which is used while registration...')
        client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=password,
            Permanent=True
        )
        return user_id
    else: 
        return None, None
    
def validate_user(username, password):
    try:
        _, app_client_id = create_user_pool_if_not_exists(user_pool_name)
        
        response = client.initiate_auth(
            ClientId=app_client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return response['AuthenticationResult']['AccessToken']
    except Exception as e:
        return None
    
