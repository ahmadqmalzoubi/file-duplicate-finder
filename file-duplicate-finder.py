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
    BUF_SIZE = 4096
    sum = hashlib.blake2b()
    with open(filename, 'rb') as f:
        data = f.read(BUF_SIZE)
        sum.update(data)
    
    return sum.hexdigest()


def blake2bsum_last4k(filename):
    sum = hashlib.blake2b()
    with open(filename, 'rb') as f:
        f.seek(-50, os.SEEK_END)
        data = f.read()
        sum.update(data)
    
    return sum.hexdigest()


parser = argparse.ArgumentParser(description='Find the duplicate files and store them in a python dictionary')
parser.add_argument('--dir', help='path of the directory to search for file duplicates')
args = parser.parse_args()


blake2b_index_dict = {}

for file in get_files_recursively(args.dir):
    if os.stat(file.path).st_size > 4096:
        blake2b_index_dict.setdefault(blake2bsum_first4k(file.path), []).append(file.path)


duplicate_blake2b_dict_first4k = {}

for key, values in blake2b_index_dict.items():
    if len(values) > 1:
        duplicate_blake2b_dict_first4k[key] = values


duplicate_blake2b_dict_last4k = {}

for key, values in duplicate_blake2b_dict_first4k.items():
    for value in values:
        duplicate_blake2b_dict_last4k.setdefault(blake2bsum_last4k(value), []).append(value)

print("\n# Duplicates:\n")
for hash, files in duplicate_blake2b_dict_last4k.items():
    print("hash: ", hash)
    for file in files:
        print(file)
    print("")

number_of_groups = len(duplicate_blake2b_dict_last4k)
number_of_all_files = 0
for files in duplicate_blake2b_dict_last4k.values():
    for file in files:
        number_of_all_files += 1
number_of_duplicate_files = number_of_all_files - number_of_groups

print(f"There are {number_of_groups} groups of duplicate files with {number_of_all_files} total number of files in these groups, whereof {number_of_duplicate_files} are duplicates.\n")