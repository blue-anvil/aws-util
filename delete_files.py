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
print(f"Delete current version of {len(keys)} files in s3://{args.bucket}/ ?")
print("(Old versions will remain. Use nuke-bucket to remove everything.)")
print("--- WARNING WARNING WARNING ---")
print("--- WARNING WARNING WARNING ---")
print("--- WARNING WARNING WARNING ---")
answer = input("(y/n): ")
if answer.lower() != 'y':
    print("Aborted.")
    exit()

s3 = boto3.client('s3')
chunk_size = 1000
deleted = 0

for i in range(0, len(keys), chunk_size):
    chunk = [{'Key': k} for k in keys[i:i + chunk_size]]
    s3.delete_objects(Bucket=args.bucket, Delete={'Objects': chunk})
    deleted += len(chunk)
    print(f"Deleted {deleted}/{len(keys)}...")

print(f"Done. {len(keys)} files removed from current view.")
