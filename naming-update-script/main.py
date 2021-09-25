#!/usr/bin/env python
from dataclasses import dataclass
from typing import List
from datetime import datetime
import ipfshttpclient
import requests
import dotenv
import json
import time
import os


dotenv.load_dotenv()

SUBGRAPH_URI = os.environ.get("SUBGRAPH_URI", "")
IPFS_API = os.environ.get("IPFS_API", "")

from logger import logger

# from backoff import retry_with_backoff

MAX_SKIP = 9_000
STEP = 1_000

DEFAULT_DESCRIPTION = "Rumble Kong League is a competitive 3 vs 3 basketball experience, combining play-to-earn functionality with NFT Collection mechanics, enabling users to compete in engaging ways through NFTs."


@dataclass(frozen=True)
class KongMeta:
    token_id: int
    name: str
    description: str


def query_kongs(skip: int) -> str:
    return (
        """
        {
          kongs(
            orderBy: id,
            orderDirection: desc,
            first: 1000,
            skip: %s
          ) {
            id
            name {
              value
            }
            bio {
              value
            }
          }
        }
        """
        % skip
    )


def _build_kong_meta(kong_meta_json: dict) -> KongMeta:
    return KongMeta(
        token_id=int(kong_meta_json["name"].split(" ")[-1][1:]),
        name=kong_meta_json["name"],
        description=kong_meta_json["description"],
    )


def _sort_by_id(original: List[KongMeta]) -> KongMeta:
    return sorted(original, key=lambda k: k.token_id)


def _save_kongs(
    *,
    pre_diff_kongs: List[KongMeta],
    post_diff_kongs: List[KongMeta],
) -> None:
    """
    On every full update (be it daily or otherwise), tracks which kongs
    have changed the name / bio. This is useful in case a mistake will
    be made down the line, and meta needs reverting. This is unlikely,
    since it is trivial to pull the names and bios of all of the kongs
    at any point in time. This function has auditability usefulness,
    nevertheless.
    """
    now = datetime.now()
    now_time = f"{now.day}-{now.month}-{now.year}::{now.hour}:{now.minute}"

    save_to_prefix = f"historical/{now_time}/diff"

    with open(f"{save_to_prefix}/pre_update_kongs.json", "w+") as f:
        f.write(json.dumps(list(map(lambda x: x.__dict__, pre_diff_kongs)), indent=4))

    with open(f"{save_to_prefix}/post_update_kongs.json", "w+") as f:
        f.write(json.dumps(list(map(lambda x: x.__dict__, post_diff_kongs)), indent=4))


def get_ipfs_kongs() -> List[KongMeta]:
    logger.debug("[START] getting ipfs kongs")

    all_folders = os.listdir("historical")
    breakpoint()
    all_folders_dates = sorted(
        map(lambda x: datetime.strptime(x, "%d-%m-%Y::%H:%M:%S"), all_folders),
        reverse=True,
    )
    latest_folder = all_folders_dates[-1]

    # build all kongs from the latest folder
    #  return all kongs
    # later on, only update the required ones in this list directly, inplace
    # and add and pin with wrapped directory on IPFS infura
    # finally check grafana and set up a cron job on aws server for this bad boy


# item looks like this: {'bio': [], 'id': '9902', 'name': [{'value': 'King Kong Bron'}]}
def _build_description(item):
    if len(item["bio"]) == 0:
        return DEFAULT_DESCRIPTION
    return item["bio"][-1]["value"]


def _build_name(item):
    kong_id = item["id"]
    if len(item["name"]) == 0:
        return f"Kong #{kong_id}"
    last_name = item["name"][-1]["value"]
    return f"{last_name} #{kong_id}"


def get_naming_contract_kongs() -> List[KongMeta]:
    logger.debug("[START] getting named kongs")

    skip = 0
    results = []

    def _prepare(_skip: int) -> List:
        query = query_kongs(_skip)
        body = {"query": query}
        res = requests.post(SUBGRAPH_URI, json=body)
        res.raise_for_status()

        if "data" in res.json():
            return res.json()["data"]["kongs"]

        return []

    while skip <= MAX_SKIP:
        results += _prepare(skip)
        skip += STEP

    all_meta = set(
        map(
            lambda x: _build_kong_meta(
                {
                    "name": _build_name(x),
                    "description": _build_description(x),
                }
            ),
            results,
        )
    )

    logger.debug("[END] getting named kongs")
    return _sort_by_id(all_meta)


def update_metadata(
    *, ipfs_kongs: List[KongMeta], contract_kongs: List[KongMeta]
) -> None:
    def update_ipfs_meta(kongs: List[KongMeta]) -> None:
        # TODO: implement
        ...

    pre_update_kongs = []
    post_update_kongs = []

    for kong in contract_kongs:
        equivalent_ipfs_kong = ipfs_kongs[kong.token_id]
        if hash(equivalent_ipfs_kong) != hash(kong):
            pre_update_kongs.append(equivalent_ipfs_kong)
            post_update_kongs.append(kong)

    _save_kongs(pre_update_kongs=pre_update_kongs, post_update_kongs=post_update_kongs)

    update_ipfs_meta(post_update_kongs)


def main():
    get_ipfs_kongs()
    # contract_kongs = get_naming_contract_kongs()
    # update_metadata(ipfs_kongs=ipfs_kongs, contract_kongs=contract_kongs)


if __name__ == "__main__":
    # todo: try except like this https://stackoverflow.com/questions/36523984/python-try-except-keep-trying-until-no-errors/36524008
    main()


# def get_ipfs_kongs(ipfs_meta_root: str) -> List[KongMeta]:
#     """
#     This script downloads all the meta that sits in ipfs_meta_root.
#     Daily via cron job, we will be re-uploading the metadata for ALL
#     the kongs. And we will then use root's hash to update the URI
#     on the contract.

#     We will not be downloading the metadata (only the first time).
#     The files will also help us track the meta diff, in case we need
#     to revert.
#     """
#     logger.debug("[START] getting ipfs kongs")

#     # TODO: ipfshttpclient is quite slow with their PRs, therefore I had to fork
#     # TODO: their codebase, and allow for the latest minor version 0.9.1
#     # TODO: check their repo from time to time to remove the dep on my git
#     client = ipfshttpclient.connect(IPFS_API)

#     @retry_with_backoff(retries=10, backoff_in_seconds=1, logger=logger)
#     def cat(cid: str) -> bytes:
#         logger.debug(f"catting cid: {cid}")
#         res = client.cat(cid)
#         time.sleep(0.01)
#         return res

#     # this pulls all the hashes of the meta jsons
#     # we need to pull the hashes like this, because each time we update the name / bio
#     # the meta's hash will change
#     all_meta = client.ls(ipfs_meta_root)["Objects"][0]["Links"]
#     all_meta = list(map(lambda x: x["Hash"], all_meta))
#     all_meta_len_pre = len(all_meta)

#     # ! this cat sometimes throws a connection error. exponential backoff for individual cats
#     # this loops through all of the meta jsons and parses them
#     all_meta = set(map(lambda x: _build_kong_meta(json.loads(cat(x))), all_meta))
#     all_meta_len_post = len(all_meta)

#     assert all_meta_len_pre == all_meta_len_post, "meta len not equal"

#     client.close()
#     del client

#     logger.debug("[END] getting ipfs kongs")
#     return _sort_by_id(all_meta)
