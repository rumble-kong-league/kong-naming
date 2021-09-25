#!/usr/bin/env python
from typing import List, Tuple, Dict
from dataclasses import dataclass
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

DATE_FORMAT = "%d-%m-%Y::%H:%M:%S"
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

    with open(f"{save_to_prefix}/pre.json", "w") as f:
        f.write(json.dumps(list(map(lambda x: x.__dict__, pre_diff_kongs)), indent=4))

    with open(f"{save_to_prefix}/post.json", "w") as f:
        f.write(json.dumps(list(map(lambda x: x.__dict__, post_diff_kongs)), indent=4))


def get_ipfs_kongs() -> Tuple[Dict, List[KongMeta]]:
    logger.debug("[START] getting ipfs kongs")

    def path_to_meta(latest_folder: datetime) -> str:
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "historical",
                f"{latest_folder.day}-{latest_folder.month}-{latest_folder.year}::{latest_folder.hour}:{latest_folder.minute}:{latest_folder.second}",
                "meta",
            )
        )

    def file_to_json(ix: str, latest_folder: datetime) -> Dict:
        _path_to_meta = path_to_meta(latest_folder)
        return json.loads(open(os.path.join(_path_to_meta, ix), "r").read())

    all_folders = os.listdir("historical")
    all_folders_dates = sorted(
        map(lambda x: datetime.strptime(x, DATE_FORMAT), all_folders),
        reverse=True,
    )
    latest_folder = all_folders_dates[-1]

    all_meta = os.listdir(path_to_meta(latest_folder))
    full_meta_ipfs_kongs = list(map(lambda x: file_to_json(x, latest_folder), all_meta))
    full_meta_ipfs_kongs = list(
        sorted(full_meta_ipfs_kongs, key=lambda x: int(x["name"].split(" ")[-1][1:]))
    )
    all_ipfs_kongs = list(map(lambda x: _build_kong_meta(x), full_meta_ipfs_kongs))

    return (full_meta_ipfs_kongs, all_ipfs_kongs)


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
    # only update the required ones in this list directly, inplace
    # and add and pin with wrapped directory on IPFS infura
    # finally check grafana and set up a cron job on aws server for this bad boy

    pre_update_kongs = []
    post_update_kongs = []

    for kong in contract_kongs:
        equivalent_ipfs_kong = ipfs_kongs[kong.token_id]
        if hash(equivalent_ipfs_kong) != hash(kong):
            pre_update_kongs.append(equivalent_ipfs_kong)
            post_update_kongs.append(kong)

    _save_kongs(pre_update_kongs=pre_update_kongs, post_update_kongs=post_update_kongs)


def main():
    full_meta_kongs, ipfs_kongs = get_ipfs_kongs()
    contract_kongs = get_naming_contract_kongs()
    update_metadata(ipfs_kongs=ipfs_kongs, contract_kongs=contract_kongs)


if __name__ == "__main__":
    main()


# * for reference (ipfs)
# def get_ipfs_kongs(ipfs_meta_root: str) -> List[KongMeta]:
#     client = ipfshttpclient.connect(IPFS_API)
#     @retry_with_backoff(retries=10, backoff_in_seconds=1, logger=logger)
#     def cat(cid: str) -> bytes:
#         logger.debug(f"catting cid: {cid}")
#         res = client.cat(cid)
#         time.sleep(0.01)
#         return res
#     all_meta = client.ls(ipfs_meta_root)["Objects"][0]["Links"]
#     all_meta = list(map(lambda x: x["Hash"], all_meta))
#     all_meta_len_pre = len(all_meta)
#     all_meta = set(map(lambda x: _build_kong_meta(json.loads(cat(x))), all_meta))
#     all_meta_len_post = len(all_meta)
#     assert all_meta_len_pre == all_meta_len_post, "meta len not equal"
#     client.close()
#     del client
#     return _sort_by_id(all_meta)
