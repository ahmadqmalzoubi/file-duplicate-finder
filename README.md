# file-duplicate-finder
Python code to find duplicate files in a base directory. blake2b hash is used to find the duplicates. The code returns the number of the duplicate files with their full path names.

The problem of handling duplicate files is not new. It is a very known problem and many programmers created tools to find duplicates and then run some actions on the duplicate files.
There are different approaches to tackle this problem and each one has its own strength points. In this script, the algorithm used is a simple one: Scan base directory recuresively for all the files, then:
  - check file size
  - size exist in fileDict?
    - yes: then calculate the file hash of first 4kB of the file
      - file hash exist in fileDict[size]?
        - yes: then append the filePathName to the fileDict[size][hash] list of filePathName values.
        - no: then create fileDict[size][hash] list and add fileName to its list of values.
    - no: then create fileDict[size] and calculate the file hash of first 4k
      - create fileDict[size][hash] list and add filePathName to its list of values.
     
The cryptographic hash function used in this script is BLAKE2(blake2b), see https://www.blake2.net/ for more details.
