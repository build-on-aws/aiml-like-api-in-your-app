import boto3
import os



def lambda_handler(event, context):
    print (event)

    region_name = os.environ.get('ENV_REGION_NAME')
    rekognition = boto3.client('rekognition')
    SNS_REKOGNITION = os.environ.get('ENV_SNS_REKOGNITION')
    SNS_ROLE_ARN_REKOGNITION = os.environ.get('ENV_SNS_ROLE_ARN_REK')


    for record in event['Records']:

        #Leemos el archivo en S3

        bucket1 = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        filename = key.split('/')[-1]

        print('Empieza la lectura de {}'.format(filename)) 

        #Rekognition Content Moderation APIs
        #https://docs.aws.amazon.com/cli/latest/reference/rekognition/start-content-moderation.html
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.start_content_moderation

        startModerationLabelDetection = rekognition.start_content_moderation(
            Video={'S3Object': {
                     'Bucket': bucket1, 
                       'Name': filename, }
                },
            NotificationChannel= {
            'SNSTopicArn': SNS_REKOGNITION,
            'RoleArn'    : SNS_ROLE_ARN_REKOGNITION
                                })

        moderationJobId = startModerationLabelDetection['JobId']
        print("Job Id: {0}".format(moderationJobId))

        #get content moderation
        #https://docs.aws.amazon.com/cli/latest/reference/rekognition/get-content-moderation.html

        getContentModeration = rekognition.get_content_moderation(
            JobId=moderationJobId,
            SortBy='TIMESTAMP')


        print("Procesando....")

 
        results = [{
            'taskId': moderationJobId,
            'resultCode': 'Procesando',
            'resultString': 'Procesando'
        }]

    return {
        #'invocationSchemaVersion': invocationSchemaVersion,
        'treatMissingKeysAs': 'PermanentFailure',
        #'invocationId': invocationId,
        'results': results
    }