import boto3
import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-b', '--bucket', required=True)
parser.add_argument('-p', '--prefix', default='')
parser.add_argument('-f', '--file', required=True)
parser.add_argument('-t', '--test', action='store_true', default=False)
parser.add_argument('-w', '--workers', type=int, default=10)
args = parser.parse_args()

s3 = boto3.client('s3')
paginator = s3.get_paginator('list_objects_v2')

keys = [
    obj['Key']
    for page in paginator.paginate(Bucket=args.bucket, Prefix=args.prefix)
    for obj in page.get('Contents', [])
]

if args.test:
    for key in keys:
        print(key)
else:
    def hash_key(key):
        client = boto3.client('s3')
        response = client.get_object(Bucket=args.bucket, Key=key)
        sha256 = hashlib.sha256()
        for chunk in response['Body'].iter_chunks(chunk_size=65536):
            sha256.update(chunk)
        return f"{sha256.hexdigest()}  {key}"

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        lines = list(executor.map(hash_key, keys))

    for line in lines:
        print(line)
    open(args.file, 'w').write('\n'.join(lines))
