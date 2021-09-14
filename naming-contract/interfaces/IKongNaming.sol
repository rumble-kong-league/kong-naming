//SPDX-License-Identifier: MIT
pragma solidity =0.8.7;

interface IKongNaming {
    event SetName(uint256 indexed tokenID, bytes32 name);

    event SetBio(uint256 indexed tokenID, string bio);

    function setName(bytes32 name, uint256 tokenID) external payable;

    function setBio(string memory bio, uint256 tokenID) external payable;
}
