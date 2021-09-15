#!/usr/bin/env python
import requests

SUBGRAPH_URI = "https://api.studio.thegraph.com/query/3020/kong-naming/0.0.2"

def query_kongs(qty: int, skip: int) -> str:
  return """{
  kongs(
    orderBy: id,
    orderDirection: desc,
    first: """ + str(qty) + """,
    skip: """ + str(skip) + """
  ) {
    id
    name {
      value
    }
    bio {
      value
    }
  }
}"""

def main():
  # check the names and bios of every kong
  # check the metadata and check the difference
  # for the ones that you have pulled that have different names / bio
  #    update the metadata with the new info
  ...
