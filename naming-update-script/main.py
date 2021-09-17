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

MAX_SKIP = 9_000
STEP = 1_000


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


# * saves the kongs, in case we ever need to revert
def _save_kongs(
    *, pre_update_kongs: List[KongMeta], post_update_kongs: List[KongMeta]
) -> None:
    now = datetime.now()
    now_time = f"{now.day}-{now.month}-{now.year}::{now.hour}:{now.minute}"

    pre_update_kongs = list(map(lambda x: x.__dict__, pre_update_kongs))
    post_update_kongs = list(map(lambda x: x.__dict__, post_update_kongs))

    with open(f"historical/{now_time}_pre_update_kongs.json", "w+") as f:
        f.write(json.dumps(pre_update_kongs, indent=4))

    with open(f"historical/{now_time}_post_update_kongs.json", "w+") as f:
        f.write(json.dumps(post_update_kongs, indent=4))


def get_ipfs_kongs() -> List[KongMeta]:
    client = ipfshttpclient.connect(IPFS_API)

    def cat(cid: str) -> bytes:
        res = client.cat(cid)
        time.sleep(0.001)
        return res

    # this pulls all the hashes of the meta jsons
    root_meta_dir = "QmZmghtNCGYx496Dq2U9nHuxqSbSLhNuXpFPPz6eA2urME"
    all_meta = client.ls(root_meta_dir)["Objects"][0]["Links"]
    all_meta = list(map(lambda x: x["Hash"], all_meta))
    all_meta_len_pre = len(all_meta)

    # ! this cat sometimes throws a connection error. exponential backoff for individual cats
    # this loops through all of the meta jsons and parses them
    all_meta = set(map(lambda x: _build_kong_meta(json.loads(cat(x))), all_meta))
    all_meta_len_post = len(all_meta)

    assert all_meta_len_pre == all_meta_len_post, "meta len not equal"

    client.close()
    del client

    return _sort_by_id(all_meta)


def get_naming_contract_kongs() -> List[KongMeta]:
    skip = 0
    results = []

    def _prepare(_skip: int) -> None:
        query = query_kongs(_skip)
        body = {"query": query}
        res = requests.post(SUBGRAPH_URI, json=body)
        res.raise_for_status()
        kongs = []
        if "data" in res.json():
            kongs = res.json()["data"]["kongs"]
        if len(kongs) == 0:
            return
        results.append(*kongs)

    while skip <= MAX_SKIP:
        _prepare(skip)
        skip += STEP

    all_meta = set(
        map(
            lambda x: _build_kong_meta(
                {
                    "name": f"{x['name'][-1]['value']} #{x['id']}",
                    "description": x["bio"][-1]["value"],
                }
            ),
            results,
        )
    )

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
    ipfs_kongs = get_ipfs_kongs()
    contract_kongs = get_naming_contract_kongs()
    update_metadata(ipfs_kongs=ipfs_kongs, contract_kongs=contract_kongs)


if __name__ == "__main__":
    # todo: try except like this https://stackoverflow.com/questions/36523984/python-try-except-keep-trying-until-no-errors/36524008
    main()
