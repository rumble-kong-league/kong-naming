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


@dataclass(frozen=True)
class KongMeta:
    name: str
    description: str


def query_kongs(qty: int, skip: int) -> str:
    return (
        """
        {
          kongs(
            orderBy: id,
            orderDirection: desc,
            first: %s,
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
        % qty,
        skip,
    )


def _build_kong_meta(kong_meta_json: dict) -> KongMeta:
    return KongMeta(
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
    ...


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
