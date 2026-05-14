import boto3
import argparse
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    _local = threading.local()

    def hash_key(key):
        if not hasattr(_local, 'client'):
            _local.client = boto3.client('s3')
        response = _local.client.get_object(Bucket=args.bucket, Key=key)
        sha256 = hashlib.sha256()
        for chunk in response['Body'].iter_chunks(chunk_size=8 * 1024 * 1024):
            sha256.update(chunk)
        return f"{sha256.hexdigest()}  {key}"

    lines = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(hash_key, key): key for key in keys}
        for future in as_completed(futures):
            line = future.result()
            lines.append(line)
            print(line)

    open(args.file, 'w').write('\n'.join(lines))
