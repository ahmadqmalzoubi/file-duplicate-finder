#!/usr/bin/env python3

import os
import hashlib
import argparse


def get_files_recursively(baseDir):
    for dentry in os.scandir(baseDir):
        if dentry.is_dir(follow_symlinks=False):
            yield from get_files_recursively(dentry.path)
        else:
            yield dentry


def blake2bsum_first4k(filename):
    buffer_size = 4096
    sum = hashlib.blake2b()
    with open(filename, 'rb') as f:
        data = f.read(buffer_size)
        sum.update(data)

    return sum.hexdigest()


def blake2bsum_last4k(filename):
    sum = hashlib.blake2b()
    with open(filename, 'rb') as f:
        f.seek(-4096, os.SEEK_END)
        data = f.read()
        sum.update(data)

    return sum.hexdigest()


parser = argparse.ArgumentParser(
    description='Find the duplicate files and store them in a python dictionary')
parser.add_argument('basedir', nargs='?', default=".",
                    help='path of the directory to search for file duplicates')
parser.add_argument('--minsize', nargs='?', default=4096, type=int,
                    help='minumum size in bytes of the files to be searched')
parser.add_argument('--maxsize', nargs='?', default=4294967296, type=int,
                    help='maximum size in bytes of the files to be searched')
args = parser.parse_args()


base_dir = args.basedir
file_max_size = args.maxsize
file_min_size = args.minsize

files_dict = {}

for file in get_files_recursively(base_dir):
    if os.stat(file.path).st_size > 0 and os.stat(file.path).st_size > file_min_size and os.stat(file.path).st_size < file_max_size:
        if os.stat(file.path).st_size in files_dict:
            if blake2bsum_first4k(file.path) in files_dict[os.stat(file.path).st_size]:
                files_dict[os.stat(file.path).st_size][blake2bsum_first4k(
                    file.path)].append(file.path)
            else:
                files_dict[os.stat(file.path).st_size][blake2bsum_first4k(
                    file.path)] = []
                files_dict[os.stat(file.path).st_size][blake2bsum_first4k(
                    file.path)].append(file.path)
        else:
            files_dict[os.stat(file.path).st_size] = {}
            files_dict[os.stat(file.path).st_size][blake2bsum_first4k(
                file.path)] = []
            files_dict[os.stat(file.path).st_size][blake2bsum_first4k(
                file.path)].append(file.path)

duplicate_files_dict = {}

for size, hashes_dict in files_dict.items():
    for hash in hashes_dict:
        if len(files_dict[size][hash]) > 1:
            if size in duplicate_files_dict:
                duplicate_files_dict[size][hash] = files_dict[size][hash]
            else:
                duplicate_files_dict[size] = {}
                duplicate_files_dict[size][hash] = files_dict[size][hash]


number_of_groups = 0
number_of_all_files = 0

print("\n# Duplicates:\n")
print("File Size\tFiles Hash with the list of duplicate files\n")

for size, hashes_dict in duplicate_files_dict.items():
    print(size)
    for hash in hashes_dict:
        number_of_groups += 1
        number_of_all_files += len(hashes_dict[hash])
        print("\t", hash)
        print("\t", hashes_dict[hash])
        print("")
    print("")

number_of_duplicate_files = number_of_all_files - number_of_groups

print(
    f"\n## Searching for duplicate files in the Base Directory: {base_dir} ->\n")

print(
    f"There are {number_of_groups} groups of duplicate files with \
{number_of_all_files} total number of files in these groups, whereof \
{number_of_duplicate_files} are duplicates.\n")
