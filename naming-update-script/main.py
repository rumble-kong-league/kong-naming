#!/usr/bin/env python
from dataclasses import dataclass
from typing import Set
import ipfshttpclient
import requests
import dotenv
import json
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


def get_ipfs_kongs() -> Set[KongMeta]:
    client = ipfshttpclient.connect(IPFS_API)

    # this pulls all the hashes of the meta jsons
    root_meta_dir = "QmZmghtNCGYx496Dq2U9nHuxqSbSLhNuXpFPPz6eA2urME"
    all_meta = client.ls(root_meta_dir)["Objects"][0]["Links"]
    all_meta = list(map(lambda x: x["Hash"], all_meta))
    all_meta_len_pre = len(all_meta)

    # this loops through all of the meta jsons and parses them
    all_meta = set(map(lambda x: _build_kong_meta(json.loads(client.cat(x))), all_meta))
    all_meta_len_post = len(all_meta)

    assert all_meta_len_pre == all_meta_len_post, "meta len not equal"

    client.close()
    del client

    return all_meta


def get_naming_contract_kongs() -> Set[KongMeta]:
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

    return all_meta


def update_metadata(
    *, ipfs_kongs: Set[KongMeta], contract_kongs: Set[KongMeta]
) -> None:
    # returns all the ipfs metadata on each kong
    ...


def main():
    ipfs_kongs = get_ipfs_kongs()
    breakpoint()
    # contract_kongs = get_naming_contract_kongs()
    # update_metadata(ipfs_kongs=ipfs_kongs, contract_kongs=contract_kongs)


if __name__ == "__main__":
    main()
