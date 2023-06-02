import boto3
import time

import os
import time
import json

region_name = os.environ.get('ENV_REGION_NAME')
SNS_ARN = os.environ.get('ENV_SNS_REKOGNITION')
bucket_key_moderation = os.environ.get('BUCKET_KEY_MODERATION')
bucket_name = os.environ.get('BUCKET_NAME')

s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')

def procesa_sns (record):

    body = record["Sns"]
    print ("body: {}".format(body))
    message = json.loads(body['Message'])
    print ("Message: {}".format(message))
    request = {}

    request["jobId"] = message['JobId']
    request["Timestamp"] = message['Timestamp']
    request["jobStatus"] = message['Status']
    request["jobAPI"] = message['API']
    request["bucketName"] = message['Video']['S3Bucket']
    request["objectName"] = message['Video']['S3ObjectName']

    print ("Message de SNS: {}".format(request))

    return request

base_path="/tmp/"

def upload_json_to_s3(json_data, bucket_name, file_key, content_type):

    try:
        # Convert the JSON data to bytes
        file_bytes = json.dumps(json_data).encode('utf-8')

        # Upload the JSON file to S3
        response = s3_client.put_object(Body=file_bytes, Bucket=bucket_name, Key=file_key, ContentType=content_type)

        print(f"JSON data uploaded to S3: {bucket_name}/{file_key}")

        return f"s3://{bucket_name}/{file_key}"

    except Exception as e:
        print(f"Error uploading JSON data to S3: {e}")
        raise


def lambda_handler(event, context):
    print (event)


    for record in event['Records']:

        request= procesa_sns (record) 
        moderationJobId = request["jobId"]
        filename = request["objectName"]

        print ("moderationJobId: {}".format(moderationJobId))
        print ("filename: {}".format(filename))

        #get content moderation
        #https://docs.aws.amazon.com/cli/latest/reference/rekognition/get-content-moderation.html

        getContentModeration = rekognition_client.get_content_moderation(
            JobId=moderationJobId,
            SortBy='TIMESTAMP')

        while (getContentModeration['JobStatus'] == 'IN_PROGRESS'):
            time.sleep(5)
            print('.', end='')

            getContentModeration = rekognition_client.get_content_moderation(
                JobId=moderationJobId,
                SortBy='TIMESTAMP')

        print(getContentModeration['JobStatus'])
        print(getContentModeration)

        theObjects = {}

        strDetail = "Moderation labels in video\n"
        strOverall = "Moderation labels in the overall video:\n"

        # Potentially unsafe content detected in each frame
        for obj in getContentModeration['ModerationLabels']:
            ts = obj["Timestamp"]
            cconfidence = obj['ModerationLabel']["Confidence"]
            oname = obj['ModerationLabel']["Name"]
            strDetail = strDetail + "At {} ms: {} (Confidence: {})\n".format(ts, oname, round(cconfidence, 2))
            if oname in theObjects:
                cojb = theObjects[oname]
                theObjects[oname] = {"Name": oname, "Count": 1 + cojb["Count"]}
            else:
                theObjects[oname] = {"Name": oname, "Count": 1}

        # Unique objects detected in video
        for theObject in theObjects:
            strOverall = strOverall + "Name: {}, Count: {}\n".format(theObject, theObjects[theObject]["Count"])

        # Display results
        print(strOverall)

        filename = filename.replace(".mp4", ".json")
        key = bucket_key_moderation + "/" + filename

        upload_json_to_s3(getContentModeration["ModerationLabels"], bucket_name, key, "application/json")


        results = [{
            'taskId': moderationJobId,
            'resultCode': 'Succeeded',
            'resultString': 'Succeeded'
        }]

    return {
        'treatMissingKeysAs': 'PermanentFailure',
        'results': results
    }