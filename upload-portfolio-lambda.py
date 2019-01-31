import json
import boto3
from io import BytesIO
import zipfile
import mimetypes

def lambda_handler(event, context):

    s3 = boto3.resource('s3')

    portfolio_bucket = s3.Bucket('portfolio.tejaswivenupalli.info')
    build_bucket = s3.Bucket('portfoliobuild.tejaswi.info')

    portfolio_zip = BytesIO()
    build_bucket.download_fileobj('portfoliobuild.zip',portfolio_zip)

    with zipfile.ZipFile(portfolio_zip) as myzip:
        for name in myzip.namelist():
            obj = myzip.open(name)
            portfolio_bucket.upload_fileobj(obj,name,
            ExtraArgs={'ContentType':mimetypes.guess_type(name)[0]})
            portfolio_bucket.Object(name).Acl().put(ACL="public-read")
    return "Hello From Lambda"
