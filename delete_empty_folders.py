import boto3
import argparse

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-b', '--bucket', required=True)
parser.add_argument('-p', '--prefix', default='')
parser.add_argument('-t', '--test', action='store_true', default=False)
args = parser.parse_args()

s3 = boto3.client('s3')
paginator = s3.get_paginator('list_objects_v2')

print("Scanning bucket...")
file_keys = set()
folders = []

for page in paginator.paginate(Bucket=args.bucket, Prefix=args.prefix):
    for obj in page.get('Contents', []):
        key = obj['Key']
        if key.endswith('/'):
            folders.append(key)
        else:
            file_keys.add(key)

empty_folders = [f for f in folders if not any(k.startswith(f) for k in file_keys)]

if not empty_folders:
    print("No empty folders found.")
    exit()

if args.test:
    for f in empty_folders:
        print(f"s3://{args.bucket}/{f}")
    print(f"\n{len(empty_folders)} empty folders would be deleted.")
    exit()

print(f"Found {len(empty_folders)} empty folders.")
answer = input("Delete them? (y/n): ")
if answer.lower() != 'y':
    print("Aborted.")
    exit()

chunk_size = 1000
deleted = 0
for i in range(0, len(empty_folders), chunk_size):
    chunk = [{'Key': k} for k in empty_folders[i:i + chunk_size]]
    s3.delete_objects(Bucket=args.bucket, Delete={'Objects': chunk})
    deleted += len(chunk)
    print(f"Deleted {deleted}/{len(empty_folders)} empty folders...")

print(f"Done. {len(empty_folders)} empty folders removed from current view.")
