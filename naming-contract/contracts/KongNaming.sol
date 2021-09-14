// SPDX-License-Identifier: MIT
pragma solidity =0.8.7;

import "../interfaces/IKongNaming.sol";
import "../interfaces/IERC721.sol";

contract KongNaming is IKongNaming {
    mapping(uint256 => bytes32) public names;
    mapping(uint256 => string) public bios;

    IERC721 public constant rkl =
        IERC721(0xEf0182dc0574cd5874494a120750FD222FdB909a);

    address public immutable admin;
    address payable public immutable beneficiary;

    constructor(address newAdmin, address payable newBeneficiary) {
        ensureAddressNotZero(newAdmin);
        ensureAddressNotZero(newBeneficiary);
        admin = newAdmin;
        beneficiary = newBeneficiary;
    }

    function setName(bytes32 name, uint256 tokenID) external override {
        // require that the caller is the owner of the kong
        // if this is not the first time that the name is set, charge a small fee
        names[tokenID] = name;
    }

    function setBio(string memory bio, uint256 tokenID) external override {
        // require that the caller is the owner of the kong
        // if this is not the first time that the bio is ser, charge a small fee
        bios[tokenID] = bio;
    }

    function ensureAddressNotZero(address checkThis) private pure {
        require(checkThis != address(0), "KongNaming::address is zero");
    }
}
