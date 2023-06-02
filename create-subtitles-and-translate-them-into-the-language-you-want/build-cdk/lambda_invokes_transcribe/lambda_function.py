import boto3
import os
import uuid


region_name = os.environ.get('ENV_REGION_NAME')
SOURCE_LANG_CODE = os.environ.get('SOURCE_LANG_CODE')

SubtitleBucketName = os.environ.get('SubtitleBucketName')
SubtitleKeyName = os.environ.get('SubtitleKeyName')
VideoBucketName = os.environ.get('VideoBucketName')

transcribe_client  = boto3.client('transcribe')

def lambda_handler(event, context):
    print (event)




    for record in event['Records']:
        print("Event: ",event['Records'])
        record = event['Records'][0]
    
        s3bucket = record['s3']['bucket']['name']
        s3object = record['s3']['object']['key']
        print("s3bucket: ",s3bucket)
        print("s3object: ",s3object)

   
        s3Path    = "s3://" + s3bucket + "/" + s3object
        jobName   = s3object + '-' + str(uuid.uuid4())
        OutputKey = SubtitleKeyName+"/"+s3object.replace(".mp4","")+"/"+SOURCE_LANG_CODE+"_"+s3object

        print('Start transcription job for s3Path: {}'.format(s3Path))
        #Read the file from S3 

        s3Path = "s3://" + s3bucket + "/" + s3object
        jobName = s3object + '-' + str(uuid.uuid4())

        print('Start transcription job for s3Path: {}'.format(s3Path))

        #Transcribe APIs
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/transcribe.html#TranscribeService.Client.start_transcription_job
        
        response = transcribe_client.start_transcription_job(
            TranscriptionJobName=jobName,
            LanguageCode= SOURCE_LANG_CODE,
            MediaFormat='mp4',
            Media={
            'MediaFileUri': s3Path
            },
            OutputBucketName = SubtitleBucketName,
            OutputKey=OutputKey.replace(".mp4",""), 
            Subtitles={
            'Formats': [
                'srt'
            ]}
            )

        TranscriptionJobName = response['TranscriptionJob']['TranscriptionJobName']
    
        print("Processing....")
        print("TranscriptionJobName : {}".format(TranscriptionJobName))

    
    return True
    
    