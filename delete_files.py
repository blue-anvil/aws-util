import boto3
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-b', '--bucket', required=True)
parser.add_argument('-f', '--file', required=True)
parser.add_argument('-t', '--test', action='store_true', default=False)
parser.add_argument('-w', '--workers', type=int, default=20)
args = parser.parse_args()

with open(args.file) as f:
    keys = [line.strip() for line in f if line.strip()]

if args.test:
    for key in keys:
        print(f"s3://{args.bucket}/{key}")
    print(f"\n{len(keys)} files would be deleted.")
    exit()

print("--- WARNING WARNING WARNING ---")
print("--- WARNING WARNING WARNING ---")
print("--- WARNING WARNING WARNING ---")
print(f"Delete all versions of {len(keys)} files in s3://{args.bucket}/ ?")
print("--- WARNING WARNING WARNING ---")
print("--- WARNING WARNING WARNING ---")
print("--- WARNING WARNING WARNING ---")
answer = input("(y/n): ")
if answer.lower() != 'y':
    print("Aborted.")
    exit()

s3 = boto3.client('s3')
paginator = s3.get_paginator('list_object_versions')

def collect_versions(key):
    objects = []
    for page in paginator.paginate(Bucket=args.bucket, Prefix=key):
        for v in page.get('Versions', []):
            if v['Key'] == key:
                objects.append({'Key': v['Key'], 'VersionId': v['VersionId']})
        for m in page.get('DeleteMarkers', []):
            if m['Key'] == key:
                objects.append({'Key': m['Key'], 'VersionId': m['VersionId']})
    return objects

all_objects = []
with ThreadPoolExecutor(max_workers=args.workers) as executor:
    futures = {executor.submit(collect_versions, key): key for key in keys}
    for future in as_completed(futures):
        all_objects.extend(future.result())

total_versions = len(all_objects)
chunk_size = 1000
deleted = 0
for i in range(0, total_versions, chunk_size):
    chunk = all_objects[i:i + chunk_size]
    s3.delete_objects(Bucket=args.bucket, Delete={'Objects': chunk})
    deleted += len(chunk)
    print(f"Deleted {deleted}/{total_versions} versions...")

print(f"Done. Deleted {total_versions} versions across {len(keys)} keys.")
