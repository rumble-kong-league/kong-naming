#!/bin/bash

sudo yum update -y
sudo yum install -y git htop golang tmux

cd ~
wget https://dist.ipfs.io/go-ipfs/v0.9.1/go-ipfs_v0.9.1_linux-amd64.tar.gz
tar -xvzf go-ipfs_v0.9.1_linux-amd64.tar.gz
cd go-ipfs
sudo bash install.sh

ipfs --version