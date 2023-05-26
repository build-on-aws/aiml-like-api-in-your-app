from aws_cdk import (
    Duration, RemovalPolicy,
    Stack,
    aws_iam,
    aws_s3 as s3,
    aws_s3_notifications,
    aws_lambda,
)
from constructs import Construct

class BuildCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        REGION_NAME = 'us-east-1'

        SOURCE_LANG_CODE = 'en-US'
        TARGET_LANG_CODE = 'es-ES'

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ Create Amazon S3 Bucket +++++++++++++++++++++++++++++++
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        VIDEO_BUCKET_NAME   = "video-bucket"
        SUBTITLE_BUCKET_NAME  = "subtitle-bucket"
        INPUT_KEY  = "subtitle_original"
        OUTPUT_KEY = "subtitle_new"

        bucket_video = s3.Bucket(self, VIDEO_BUCKET_NAME ,  versioned=False, removal_policy=RemovalPolicy.DESTROY)
        bucket_subtitle = s3.Bucket(self, SUBTITLE_BUCKET_NAME ,  versioned=False, removal_policy=RemovalPolicy.DESTROY)


        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++The Lambda function invokes Amazon Rekognition API +++++++++++++
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_invokes_transcribe= aws_lambda.Function(self, "lambda_invokes_transcribe",
                                    handler = "lambda_function.lambda_handler",
                                    timeout = Duration.seconds(300),
                                    runtime = aws_lambda.Runtime.PYTHON_3_8,
                                    memory_size = 256, description = "Lambda Funtion that invokes Amazon Transcribe API",
                                    code = aws_lambda.Code.from_asset("./lambda_invokes_transcribe"),
                                    environment = {
                                        'ENV_REGION_NAME'  : REGION_NAME,
                                        "SubtitleBucketName" : bucket_subtitle.bucket_name,
                                        "SubtitleKeyName" : INPUT_KEY,
                                        "VideoBucketName" : bucket_video.bucket_name,
                                        "SOURCE_LANG_CODE" : SOURCE_LANG_CODE}
                                        
                                    )

        lambda_invokes_transcribe.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=["transcribe:*"], 
                resources=['*'])
              )
        

        # Added read and write permission to S3 and the event that will trigger it

        bucket_video.grant_read_write(lambda_invokes_transcribe) 
        bucket_subtitle.grant_read_write(lambda_invokes_transcribe) 
        notification = aws_s3_notifications.LambdaDestination(lambda_invokes_transcribe)
        bucket_video.add_event_notification(s3.EventType.OBJECT_CREATED, notification) 
        
        #Create a IAM role for transcribe 

        transcribe_role = aws_iam.Role(self, "transcribe_role",
                                       assumed_by=aws_iam.ServicePrincipal("transcribe.amazonaws.com"),
                                       )
        bucket_subtitle.grant_write(transcribe_role) 
    
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ The Lambda function invokes Amazon Translate API ++++++++++++++++++
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_invokes_translate= aws_lambda.Function(self, "lambda_invokes_translate",
                                    handler = "lambda_function.lambda_handler",
                                    timeout = Duration.seconds(300),
                                    runtime = aws_lambda.Runtime.PYTHON_3_8,
                                    memory_size = 256, description = "Lambda Function that process the SRT delivered by amazon transcribes and translates its content",
                                    code = aws_lambda.Code.from_asset("./lambda_invokes_translate"),
                                    environment = {
                                        'ENV_REGION_NAME': REGION_NAME,
                                        "SubtitleBucketName" : bucket_subtitle.bucket_name,
                                        "SubtitleKeyName_in" : INPUT_KEY,
                                        "SubtitleKeyName_out" : OUTPUT_KEY,
                                        "SOURCE_LANG_CODE" : SOURCE_LANG_CODE[0:2],
                                        "TARGET_LANG_CODE" : TARGET_LANG_CODE[0:2]
                                        }
                                    )
                
        lambda_invokes_translate.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=["translate:*"], 
                resources=['*'])
              )

        bucket_subtitle.grant_read_write(lambda_invokes_translate) 
        notification2 = aws_s3_notifications.LambdaDestination(lambda_invokes_translate)
        bucket_subtitle.add_event_notification(s3.EventType.OBJECT_CREATED, notification2) 

