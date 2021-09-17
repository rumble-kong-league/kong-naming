#!/usr/bin/env python
from collections import dataclass
from typing import Set
import requests
import dotenv
import os

dotenv.load_dotenv()

SUBGRAPH_URI = os.environ.get("SUBGRAPH_URI", "")
IPFS_API = os.environ.get("IPFS_API", "")


@dataclass(frozen=True)
class KongMeta:
    token_id: int
    name: str
    bio: str


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


def get_ipfs_kongs() -> Set[KongMeta]:
    ...


def get_naming_contract_kongs() -> Set[KongMeta]:
    ...


def update_metadata(
    *, ipfs_kongs: Set[KongMeta], contract_kongs: Set[KongMeta]
) -> None:
    # returns all the ipfs metadata on each kong
    ...


def main():
    ipfs_kongs = get_ipfs_kongs()
    contract_kongs = get_naming_contract_kongs()
    update_metadata(ipfs_kongs=ipfs_kongs, contract_kongs=contract_kongs)
