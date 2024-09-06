import os
from flask import Flask, render_template, request, redirect, url_for, flash
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Fetch custom AWS S3 endpoint, proxy, and SSL verification settings from environment variables
s3_endpoint = os.getenv('AWS_S3_ENDPOINT', None)
http_proxy = os.getenv('HTTP_PROXY', None)
https_proxy = os.getenv('HTTPS_PROXY', None)
ignore_ssl = os.getenv('IGNORE_SSL', 'false').lower() == 'true'

# Prepare proxy configuration if proxies are defined
proxies = None
if http_proxy or https_proxy:
    proxies = {
        'http': http_proxy,
        'https': https_proxy
    }

# Initialize the S3 client with proxy support and SSL verification setting
if s3_endpoint:
    s3 = boto3.client(
        's3',
        endpoint_url=s3_endpoint,  # Custom endpoint
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        config=boto3.session.Config(proxies=proxies),
        verify=not ignore_ssl  # Enable or disable SSL verification based on IGNORE_SSL env variable
    )
else:
    s3 = boto3.client(
        's3',
        config=boto3.session.Config(proxies=proxies),
        verify=not ignore_ssl  # Enable or disable SSL verification
    )

# Home Route - Display available buckets and actions
@app.route('/')
def index():
    try:
        buckets = s3.list_buckets().get('Buckets')
    except ClientError as e:
        flash(f"Error: {e}", "danger")
        buckets = []
    return render_template('index.html', buckets=buckets)

# Create a new bucket
@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form['bucket_name']
    try:
        s3.create_bucket(Bucket=bucket_name)
        flash(f"Bucket '{bucket_name}' created successfully!", "success")
    except ClientError as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for('index'))

# Delete a bucket
@app.route('/delete_bucket/<bucket_name>')
def delete_bucket(bucket_name):
    try:
        s3.delete_bucket(Bucket=bucket_name)
        flash(f"Bucket '{bucket_name}' deleted successfully!", "success")
    except ClientError as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for('index'))

# List objects in a bucket
@app.route('/list_objects/<bucket_name>')
def list_objects(bucket_name):
    try:
        objects = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
        return render_template('bucket_objects.html', bucket_name=bucket_name, objects=objects)
    except ClientError as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
