import boto3
import argparse

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-b', '--bucket', required=True)
parser.add_argument('-f', '--file', required=True)
parser.add_argument('-t', '--test', action='store_true', default=False)
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

for key in keys:
    objects = []
    for page in paginator.paginate(Bucket=args.bucket, Prefix=key):
        for v in page.get('Versions', []):
            if v['Key'] == key:
                objects.append({'Key': v['Key'], 'VersionId': v['VersionId']})
        for m in page.get('DeleteMarkers', []):
            if m['Key'] == key:
                objects.append({'Key': m['Key'], 'VersionId': m['VersionId']})
    if objects:
        s3.delete_objects(Bucket=args.bucket, Delete={'Objects': objects})
        print(f"Deleted {len(objects)} versions: {key}")

print("Done.")
