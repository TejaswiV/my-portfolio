import json
import boto3
from io import BytesIO
import zipfile
import mimetypes
import boto3

def lambda_handler(event, context):

    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')



    location = {
        "bucketName": 'portfoliobuild.tejaswi.info',
        "objectKey": 'portfoliobuild.zip'
    }

    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]


        print ("Building portfolio from " +str(location))

        portfolio_bucket = s3.Bucket('portfolio.tejaswivenupalli.info')
        build_bucket = s3.Bucket(location["bucketName"])
        topic  = sns.Topic('arn:aws:sns:us-east-1:619199320723:deployPortfolioTopic')

        portfolio_zip = BytesIO()
        build_bucket.download_fileobj(location["objectKey"],portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for name in myzip.namelist():
                obj = myzip.open(name)
                portfolio_bucket.upload_fileobj(obj,name,
                ExtraArgs={'ContentType':mimetypes.guess_type(name)[0]})
                portfolio_bucket.Object(name).Acl().put(ACL="public-read")

        print ("Job Done!")
        topic.publish(Subject = "Portfolio Deployed", Message = "Portfolio Deployed Successfully")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId = job["id"])

    except:
         topic.publish(Subject = "Portfolio Deployment Failed", Message = "Portfolio was not Deployed Successfully")
         raise

    return "Hello From Lambda"
