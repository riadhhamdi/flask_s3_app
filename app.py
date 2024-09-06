from flask import Flask, render_template, request, redirect, url_for, flash
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize the S3 client
s3 = boto3.client('s3')

# Home Route - Display available buckets and actions
@app.route('/')
def index():
    buckets = s3.list_buckets().get('Buckets')
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
    app.run(debug=True)
