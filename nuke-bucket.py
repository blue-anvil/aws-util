import boto3
import argparse

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-t', '--test', action='store_true', default=False)
parser.add_argument('-b', '--bucket', required=True)
parser.add_argument('-p', '--prefix', default='')
args = parser.parse_args()

if not args.test:
    print("--- WARNING WARNING WARNING ---")
    print("--- WARNING WARNING WARNING ---")
    print("--- WARNING WARNING WARNING ---")
    print(f"Delete ***ALL*** versions in s3://{args.bucket}/{args.prefix} ? (y/n): ")
    print("--- WARNING WARNING WARNING ---")
    print("--- WARNING WARNING WARNING ---")
    print("--- WARNING WARNING WARNING ---")
    answer = input("(y/n): ")
    if answer.lower() != 'y':
        print("Aborted.")
        exit()

s3 = boto3.client('s3')

paginator = s3.get_paginator('list_object_versions')
for page in paginator.paginate(Bucket=args.bucket, Prefix=args.prefix):
    objects = []
    for v in page.get('Versions', []):
        objects.append({'Key': v['Key'], 'VersionId': v['VersionId']})
    for m in page.get('DeleteMarkers', []):
        objects.append({'Key': m['Key'], 'VersionId': m['VersionId']})
    if objects:
        if args.test:
            for obj in objects:
                print(obj['Key'])
        else:
            s3.delete_objects(Bucket=args.bucket, Delete={'Objects': objects})

print("Done." if not args.test else "Test done.")
