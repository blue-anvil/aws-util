import boto3
import argparse
import hashlib
import sys
import time
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

def si(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def hash_key(s3, bucket, key, retries=5):
    for attempt in range(retries):
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            sha256 = hashlib.sha256()
            for chunk in response['Body'].iter_chunks(chunk_size=8388608):
                sha256.update(chunk)
            return sha256.hexdigest()
        except (BotoCoreError, ClientError, ConnectionResetError, ConnectionError) as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-b', '--bucket', required=True)
parser.add_argument('-p', '--prefix', default='')
parser.add_argument('-f', '--file', required=True)
parser.add_argument('-t', '--test', action='store_true', default=False)
args = parser.parse_args()

s3 = boto3.client('s3', config=Config(retries={'max_attempts': 10, 'mode': 'adaptive'}))
paginator = s3.get_paginator('list_objects_v2')

keys = []
for page in paginator.paginate(Bucket=args.bucket, Prefix=args.prefix):
    for obj in page.get('Contents', []):
        key = obj['Key']
        if not key.endswith('/'):
            keys.append(key)

if args.test:
    for key in keys:
        print(key)
else:
    total = len(keys)
    bar_width = 40
    lines = []
    for i, key in enumerate(keys, 1):
        filled = int(bar_width * i // total)
        bar = '=' * filled + '>' + ' ' * (bar_width - filled - 1)
        print(f"\r[{bar}] {si(i)}/{si(total)}", end='', file=sys.stderr)
        digest = hash_key(s3, args.bucket, key)
        lines.append(f"{digest}  {key}")
    print(file=sys.stderr)
    open(args.file, 'w').write('\n'.join(lines))
