import json
import boto3
import time

# Create CloudFront client
cf = boto3.client('cloudfront')

DISTRIBUTION_ID = "EA51AZF868RKT"

def lambda_handler(event, context):
    cf.create_invalidation(
        DistributionId=DISTRIBUTION_ID,
        InvalidationBatch={
            'Paths': {
                'Quantity': 1,
                'Items': [
                    '/*'
                ]
            },
            'CallerReference': str(time.time()).replace(".", "")
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('CloudFront cache invalidated')
    }
