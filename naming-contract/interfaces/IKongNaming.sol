//SPDX-License-Identifier: MIT
pragma solidity =0.8.7;

interface IKongNaming {
    function setName(bytes32 name, uint256 tokenID) external;

    function setBio(string memory bio, uint256 tokenID) external;
}
