#!/usr/bin/env python
import requests
import json
import dotenv
import os
import time

dotenv.load_dotenv()

INFURA_USERNAME = os.environ.get("INFURA_IPFS_PROJECT_ID", "")
INFURA_PASSWORD = os.environ.get("INFURA_IPFS_PROJECT_SECRET", "")

# script to replicate the ipfs data on a different node


def replicate():
    # these are the original meta hashes
    meta_ipfs_hashes = json.loads(open("meta_ipfs_hashes.json").read())

    for count, _hash in enumerate(meta_ipfs_hashes):
        print(f"workin on {count} {_hash}")
        res = requests.post(
            f"https://ipfs.infura.io:5001/api/v0/pin/add?arg={_hash}",
            auth=(INFURA_USERNAME, INFURA_PASSWORD),
        )
        print(f"done {res.json()}")
        time.sleep(0.01)


def main():
    replicate()


if __name__ == "__main__":
    main()
