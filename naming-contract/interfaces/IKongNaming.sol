//SPDX-License-Identifier: MIT
pragma solidity =0.8.7;

interface IKongNaming {
    event SetName(uint256 indexed tokenID, bytes32 name);

    event SetBio(uint256 indexed tokenID, string bio);

    function setName(bytes32 name, uint256 tokenID) external payable;

    function batchSetName(bytes32[] memory names, uint256[] memory tokenIDs)
        external
        payable;

    function setBio(string memory bio, uint256 tokenID) external payable;

    function batchSetBio(string[] memory bios, uint256[] memory tokenIDs)
        external
        payable;

    function setNameAndBio(
        bytes32 name,
        string memory bio,
        uint256 tokenID
    ) external payable;

    function batchSetNameAndBio(
        bytes32[] memory names,
        string[] memory bios,
        uint256[] memory tokenIDs
    ) external payable;
}
