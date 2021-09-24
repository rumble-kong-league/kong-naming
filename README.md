# kong-naming

Kontrakt that lets kong naming and setting bios

This is a set of directories responsible for setting the kongs' names and bio.

First set of name and bio is free. Having meta automatically update requires running costs. Handling metadata is error-prone, and so having subsequent name and bio sets being paid handles both of these issues. The cost of setting the bio / name may change in the future, if ether price surges, or due to other factors.

The RKL team reserves the right to override the names / bio if they are deemed offensive / inappropriate.

## Tech Overview

There are three directories `naming-contract`, `naming-subgraph`, as well as `naming-update-script`. Contract is responsible for setting the names on the blockchain. Subgraph will index all the historical names, so in that way each kong will have his naming and bio provenance. Finally, the update script runs on a server, pulls the name changes from the subgraph, compares to the IPFS meta, and uploads the new meta along with the old one. It also saves which meta it has changed. New base URI for the collection is set on the contract.

## How to change the name / bio with a contract on Etherscan

TODO: add screenshots

- go to <url>
- connect to web3, with a wallet that holds the kongs
- input the name / bio
- hit write

---

LFG 👑🦍
