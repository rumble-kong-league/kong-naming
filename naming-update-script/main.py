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
) -> str:
    """
    On every full update (be it daily or otherwise), tracks which kongs
    have changed the name / bio. This is useful in case a mistake will
    be made down the line, and meta needs reverting. This is unlikely,
    since it is trivial to pull the names and bios of all of the kongs
    at any point in time. This function has auditability usefulness,
    nevertheless.
    """
    now = datetime.now()
    now_time = f"{now.day}-{now.month}-{now.year}::{now.hour}:{now.minute}:{now.second}"

    save_to_prefix = f"historical/{now_time}/diff"

    if not os.path.exists(save_to_prefix):
        os.makedirs(save_to_prefix)

    with open(f"{save_to_prefix}/pre.json", "w") as f:
        f.write(json.dumps(list(map(lambda x: x.__dict__, pre_diff_kongs)), indent=4))

    with open(f"{save_to_prefix}/post.json", "w") as f:
        f.write(json.dumps(list(map(lambda x: x.__dict__, post_diff_kongs)), indent=4))

    return now_time


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


def get_ipfs_kongs() -> Tuple[Dict, List[KongMeta]]:
    logger.debug("[START] get_ipfs_kongs")

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

    logger.debug("[END] get_ipfs_kongs")
    return (full_meta_ipfs_kongs, all_ipfs_kongs)


def get_naming_contract_kongs() -> List[KongMeta]:
    logger.info("[START] get_naming_contract_kongs")

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

    logger.info("[END] get_naming_contract_kongs")
    return _sort_by_id(all_meta)


def upload_to_ipfs(all_meta: List[Dict]) -> Tuple[List[str], str]:
    """
    Uploads all the meta anew, wraps in a directory, and returns the directory's
    hash. This will be the new base_uri. If this function fails, call it with
    exponential_backoff. Log everything going on in this function, since it
    is the most critical piece (along with the piece that updates the base URI).
    """
    logger.info("[START] upload_to_ipfs")
    logger.info("[END] upload_to_ipfs")
    return ([], "")


def save_meta_full_set(all_meta: List[Dict], now_time: str) -> None:
    """
    Saves all the new (to be uploaded meta) to the folder for auditability
    """
    logger.info("[START] save_meta_full_set")
    save_to_prefix = f"historical/{now_time}/meta"
    if not os.path.exists(save_to_prefix):
        os.makedirs(save_to_prefix)
    for ix, meta in enumerate(all_meta):
        assert ix == int(all_meta["id"].split(" ")[-1][1:])
        with open(f"{save_to_prefix}/{ix}", "w") as f:
            f.write(json.dumps(meta, indent=4))
    logger.info("[END] save_meta_full_set")


def save_cids_full_set(cids: List[str], root_hash: str, now_time: str) -> None:
    """
    After IPFS upload, we get the cids, that we can now write into
    the cids dir, along with the root hash.
    """
    logger.info("[START] save_cids_full_set")
    save_to_prefix = f"historical/{now_time}/cids"
    if not os.path.exists(save_to_prefix):
        os.makedirs(save_to_prefix)
    with open(f"{save_to_prefix}/hashes.json", "w") as f:
        f.writes(json.dumps(cids, indent=4))
    with open(f"{save_to_prefix}/root.json", "w") as f:
        f.writes(json.dumps(list(root_hash), indent=4))
    logger.info("[END] save_cids_full_set")


def update_metadata(
    *, full_set: List[Dict], ipfs_kongs: List[KongMeta], contract_kongs: List[KongMeta]
) -> str:
    logger.info("[START] update_metadata")

    def merge_new_into_full(
        full_set: List[Dict], ipfs_kongs: List[KongMeta]
    ) -> List[Dict]:
        logger.info("[START] merge_new_into_full")
        """
        Merges the new names and bios into the full set of the meta.
        This full set is then used to re-upload to the IPFS.
        """
        for new_kong in ipfs_kongs:
            full_set[new_kong.id]["name"] = new_kong.name
            full_set[new_kong.id]["description"] = new_kong.description
        logger.info("[END] merge_new_into_full")
        return full_set

    pre_update_kongs = []
    post_update_kongs = []

    for kong in contract_kongs:
        equivalent_ipfs_kong = ipfs_kongs[kong.token_id]
        if hash(equivalent_ipfs_kong) != hash(kong):
            pre_update_kongs.append(equivalent_ipfs_kong)
            post_update_kongs.append(kong)

    now_time = _save_kongs(
        pre_diff_kongs=pre_update_kongs, post_diff_kongs=post_update_kongs
    )

    # * use now_time to populate the folder with new cids and meta
    # * after uploading the data to ipfs, get the root folder's hash
    # * add this to the cids root.json
    full_set = merge_new_into_full(full_set, ipfs_kongs)
    save_meta_full_set(full_set, now_time)

    # * use the root hash to call the function that will execute the transaction
    # * that sets the base URI
    all_cids, root_meta_hash = upload_to_ipfs(full_set)
    save_cids_full_set(all_cids, root_meta_hash)

    # * send an email with root_meta_hash to Naz

    logger.info("[END] update_metadata")
    return root_meta_hash


def execute_base_uri_update_txn(root_meta_hash: str) -> None:
    # todo: storing an encrypted private key on the cloud is so so
    # todo: make this part of the gitcoin task for the coders
    return


def main():
    full_meta_kongs, ipfs_kongs = get_ipfs_kongs()
    contract_kongs = get_naming_contract_kongs()
    update_metadata(
        full_set=full_meta_kongs, ipfs_kongs=ipfs_kongs, contract_kongs=contract_kongs
    )
    # ! part of gitcoin task. proposa a safe solution
    # execute_base_uri_update_txn(root_meta_hash="")


# todo for gitcoin / community
#
# 1. Better ipfs upload proposal. Instead of uploading the full set every time,
#        option (a)
#        implement: unpin everything pinned on the Infura IPFS node
#        pin the new meta
#        option (b)
#        implement: use IPNS to modify the meta that has changed, keeping everything
#        else untouched. Give back the new hash of the root
# 2. Propose and implement a safe way to store the ethereum EOA wallet's private key
#        on the cloud. Justify the solution.
#
# 3. Improve this main.py script in whatever way you see fit. Justify.
#
# 4. Make all of these changes on separate branches, so that I can then decide which
#        ones to merge into the codebase.
#

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
