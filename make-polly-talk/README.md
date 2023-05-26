## Make Polly Talk 🦜

### This is an example of how you can use the [Amazon Polly](https://docs.aws.amazon.com/polly/latest/dg/what-is.html) API [Boto3 Python](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/polly.html)

![Make Polly Talk"](../images/make-polly-talk.png)

Find the code here --> [make-polly-talk.ipynb](make-polly-talk.ipynb)

## 1. From a Jupyter Notebook make the call to Polly API.

Call Polly [StartSpeechSyntesisTask API](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/polly/client/start_speech_synthesis_task.html)

```python
response = polly_client.start_speech_synthesis_task(
                VoiceId='Joanna',
                OutputS3BucketName = OUT_PUT_S3_BUCKET_NAME,
                OutputS3KeyPrefix = OUT_PUT_S3_KEY_PREFIX,
                OutputFormat= OUT_PUT_FORMAT, 
                Text= TEXT,
                Engine= ENGINE)

taskId = response['SynthesisTask']['TaskId']

```

## 2. Polly stores the result in the S3 bucket.


## 3. Retrieves the audio.

Finally use the [Get speech synthesis task](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/polly/client/get_speech_synthesis_task.html) 


```python
response_task = polly_client.get_speech_synthesis_task(
    TaskId=taskId
    )
```

You can learn more about Amazon Polly with this [Code Samples](https://docs.aws.amazon.com/polly/latest/dg/sample-code-overall.html)
