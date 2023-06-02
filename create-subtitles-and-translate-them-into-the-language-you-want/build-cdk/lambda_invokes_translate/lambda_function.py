import boto3
import os


client_s3 = boto3.client('s3')
translate_client = boto3.client('translate')

region_name = os.environ.get('ENV_REGION_NAME')
SubtitleBucketName =  os.environ.get('SubtitleBucketName')
SubtitleKeyName_in = os.environ.get('SubtitleKeyName_in')
SubtitleKeyName_out = os.environ.get('SubtitleKeyName_out')

sourceLanguage = os.environ['SOURCE_LANG_CODE']
targetLanguage= os.environ['TARGET_LANG_CODE']


base_path="/tmp/"

def to_translate(text):
    translate = translate_client.translate_text( Text=text, SourceLanguageCode=sourceLanguage, TargetLanguageCode=targetLanguage)
    print("Text translate")
    result = translate['TranslatedText']
    return result


def put_file(base_path,filename, bucket, key):
    with open(base_path+filename, "rb") as data:
        client_s3.upload_fileobj(data,bucket, key+filename)
    print("Put file in s3://{}{}{}".format(bucket,key,filename))

    return True
    
def download_file(base_path,bucket, key, filename):
    with open(base_path+filename, "wb") as data:
        client_s3.download_fileobj(bucket, key, data)
    print("Download file from s3://{}{}".format(bucket,key))
    return True

def lambda_handler(event, context):
    print (event)

    for record in event['Records']:
        print("Event: ",event['Records'])
        record = event['Records'][0]
    
        s3bucket = record['s3']['bucket']['name']
        s3object = record['s3']['object']['key']
        filename = s3object.split("/")[-1]
        key = s3object.split("/")[1]+"/"
        print("s3object: ",s3object)
        print("filename: ",filename)
        print("key: ",key)

        if  s3object.split("/")[0] == SubtitleKeyName_in:
            key_out = SubtitleKeyName_out + "/" + key
    

            if(filename.endswith("srt")): 
                srt_file_out = targetLanguage + "_" + filename

                download_file(base_path,s3bucket, s3object, filename)

                with open(base_path+filename) as f:
                    str = f.readlines()

                #According to the subtitles, the subtitles are repeated every 4 lines starting in the second. 
                #Taking into account that the first line is 0.

                sub=[]
                for n in range (2,len(str),4):
                    sub.append(n)
            
                traslate_out=[]

                n=0
                for line in str:
                    if n in sub: #Only the lines that correspond to the subtitle text are translated.
                        lines_traslate=to_translate(line)
                    else:
                        lines_traslate = line
                    traslate_out.append(lines_traslate)
                    n=n+1
            
                with open(base_path+srt_file_out, 'w') as temp_file:
                    for item in traslate_out:
                        temp_file.write(item)

                put_file(base_path,srt_file_out, s3bucket, key_out)
            else:
                print("No .srt file")

        else:
            print("Skipping the file: ",s3object)
            
    return True
