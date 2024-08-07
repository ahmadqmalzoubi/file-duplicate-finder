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


blake2b_index_dict = {}

base_dir = args.basedir
file_max_size = args.maxsize
file_min_size = args.minsize

for file in get_files_recursively(base_dir):
    if os.stat(file.path).st_size > file_min_size and os.stat(file.path).st_size < file_max_size:
        blake2b_index_dict.setdefault(
            blake2bsum_first4k(file.path), []).append(file.path)


duplicate_blake2b_dict_first4k = {}

for key, values in blake2b_index_dict.items():
    if len(values) > 1:
        duplicate_blake2b_dict_first4k[key] = values


duplicate_blake2b_dict_last4k = {}

for key, values in duplicate_blake2b_dict_first4k.items():
    for value in values:
        duplicate_blake2b_dict_last4k.setdefault(
            blake2bsum_last4k(value), []).append(value)

duplicate_files_dict = {}

for key, value in duplicate_blake2b_dict_last4k.items():
    if len(values) > 1:
        duplicate_files_dict[key] = values

print("\n# Duplicates:\n")
for hash, files in duplicate_files_dict.items():
    print("hash: ", hash)
    for file in files:
        print(file)
    print("")

print(
    f"\n## Searching for duplicate files in the Base Directory: {base_dir} ->\n")
number_of_groups = len(duplicate_files_dict)
number_of_all_files = 0
for files in duplicate_files_dict.values():
    for file in files:
        number_of_all_files += 1
number_of_duplicate_files = number_of_all_files - number_of_groups

print(
    f"There are {number_of_groups} groups of duplicate files with \
{number_of_all_files} total number of files in these groups, whereof \
{number_of_duplicate_files} are duplicates.\n")
