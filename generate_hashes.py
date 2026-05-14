import boto3
import argparse
import hashlib

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-b', '--bucket', required=True)
parser.add_argument('-p', '--prefix', default='')
parser.add_argument('-f', '--file', required=True)
parser.add_argument('-t', '--test', action='store_true', default=False)
args = parser.parse_args()

s3 = boto3.client('s3')
paginator = s3.get_paginator('list_objects_v2')

lines = []
for page in paginator.paginate(Bucket=args.bucket, Prefix=args.prefix):
    for obj in page.get('Contents', []):
        key = obj['Key']
        if key.endswith('/'):
            continue
        if args.test:
            print(key)
            continue
        response = s3.get_object(Bucket=args.bucket, Key=key)
        sha256 = hashlib.sha256()
        for chunk in response['Body'].iter_chunks(chunk_size=65536):
            sha256.update(chunk)
        digest = sha256.hexdigest()
        line = f"{digest}  {key}"
        lines.append(line)
        print(line)

if not args.test:
    open(args.file, 'w').write('\n'.join(lines))
