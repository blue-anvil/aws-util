import argparse

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('file1')
parser.add_argument('file2')
parser.add_argument('-f', '--file', required=True)
args = parser.parse_args()

def parse_hashfile(path):
    entries = {}
    with open(path) as f:
        for line in f:
            line = line.rstrip('\n')
            if line:
                hash_, key = line.split(None, 1)
                entries[key] = hash_
    return entries

hashes1 = parse_hashfile(args.file1)
hashes2 = parse_hashfile(args.file2)

matches = sorted(key for key, h in hashes1.items() if hashes2.get(key) == h)

open(args.file, 'w').write('\n'.join(matches))
print(f"{len(matches)} matching files written to {args.file}")
