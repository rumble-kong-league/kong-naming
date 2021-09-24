// SPDX-License-Identifier: MIT
pragma solidity =0.8.7;

import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/security/ReentrancyGuard.sol";

import "../interfaces/IKongNaming.sol";
import "../interfaces/IERC721.sol";

// TODO: enable changing the price chargeable for kong name / bio change

contract KongNaming is IKongNaming, ReentrancyGuard {
    mapping(uint256 => bytes32) public names;
    mapping(uint256 => string) public bios;

    mapping(uint256 => bool) private nameWasSet;
    mapping(uint256 => bool) private bioWasSet;

    IERC721 public immutable rkl;
    address public immutable admin;
    address payable public immutable beneficiary;

    uint256 changePrice = 0.025 ether;

    constructor(
        address newAdmin,
        address payable newBeneficiary,
        address newRkl
    ) {
        ensureAddressNotZero(newAdmin);
        ensureAddressNotZero(newBeneficiary);
        ensureAddressNotZero(newRkl);
        admin = newAdmin;
        beneficiary = newBeneficiary;
        rkl = IERC721(newRkl);
    }

    function setName(bytes32 name, uint256 tokenID) external payable override {
        bool isOwner = isOwnerOfKong(tokenID);
        bool isAdmin = msg.sender == admin;
        require(isAdmin || isOwner, "KongNaming::unauthorized to set");

        if (nameWasSet[tokenID] == false) {
            names[tokenID] = name;
            nameWasSet[tokenID] = true;
        } else {
            if (isOwner) {
                require(
                    msg.value == changePrice,
                    "KongNaming::insufficient ether sent"
                );
            }
            names[tokenID] = name;
        }

        emit IKongNaming.SetName(tokenID, name);
    }

    function batchSetName(bytes32[] memory _names, uint256[] memory tokenIDs)
        external
        payable
        override
        nonReentrant
    {
        require(
            _names.length == tokenIDs.length,
            "KongNaming::different length names and tokenIDs"
        );
        bool ownerOfAllKongs = isOwnerOfKongs(tokenIDs);
        require(
            msg.sender == admin || ownerOfAllKongs,
            "KongNaming::not authorized"
        );

        uint256 payableSets = 0;

        for (uint256 i = 0; i < _names.length; i) {
            if (nameWasSet[tokenIDs[i]] == false) {
                names[tokenIDs[i]] = _names[i];
                nameWasSet[tokenIDs[i]] = true;
            } else {
                names[tokenIDs[i]] = _names[i];
                payableSets += 1;
            }

            emit IKongNaming.SetName(tokenIDs[i], _names[i]);
        }

        if (ownerOfAllKongs) {
            require(
                msg.value == payableSets * changePrice,
                "KongNaming::insufficient ether sent"
            );
        }
    }

    function setBio(string memory bio, uint256 tokenID)
        external
        payable
        override
    {
        bool isOwner = isOwnerOfKong(tokenID);
        bool isAdmin = msg.sender == admin;
        require(isAdmin || isOwner, "KongNaming::unauthorized to set");

        if (bioWasSet[tokenID] == false) {
            bios[tokenID] = bio;
            bioWasSet[tokenID] = true;
        } else {
            if (isOwner) {
                require(
                    msg.value == changePrice,
                    "KongNaming::insufficient ether sent"
                );
            }
            bios[tokenID] = bio;
        }

        emit IKongNaming.SetBio(tokenID, bio);
    }

    function batchSetBio(string[] memory _bios, uint256[] memory tokenIDs)
        external
        payable
        override
        nonReentrant
    {
        require(
            _bios.length == tokenIDs.length,
            "KongNaming::different length bios and tokenIDs"
        );
        bool ownerOfAllKongs = isOwnerOfKongs(tokenIDs);
        require(
            msg.sender == admin || ownerOfAllKongs,
            "KongNaming::not authorized"
        );

        uint256 payableSets = 0;

        for (uint256 i = 0; i < _bios.length; i) {
            if (bioWasSet[tokenIDs[i]] == false) {
                _bios[tokenIDs[i]] = _bios[i];
                bioWasSet[tokenIDs[i]] = true;
            } else {
                bios[tokenIDs[i]] = _bios[i];
                payableSets += 1;
            }

            emit IKongNaming.SetBio(tokenIDs[i], _bios[i]);
        }

        if (ownerOfAllKongs) {
            require(
                msg.value == payableSets * changePrice,
                "KongNaming::insufficient ether sent"
            );
        }
    }

    function setNameAndBio(
        bytes32 name,
        string memory bio,
        uint256 tokenID
    ) external payable override {
        uint256 payableSets = 0;

        bool isOwner = isOwnerOfKong(tokenID);
        require(
            msg.sender == admin || isOwner,
            "KongNaming::unauthorized to set"
        );

        if (bioWasSet[tokenID] == false) {
            bios[tokenID] = bio;
            bioWasSet[tokenID] = true;
        } else {
            bios[tokenID] = bio;
            payableSets += 1;
        }

        if (nameWasSet[tokenID] == false) {
            names[tokenID] = name;
            nameWasSet[tokenID] = true;
        } else {
            names[tokenID] = name;
            payableSets += 1;
        }

        if (isOwner) {
            require(
                msg.value == payableSets * changePrice,
                "KongNaming::insufficient ether sent"
            );
        }

        emit IKongNaming.SetName(tokenID, name);
        emit IKongNaming.SetBio(tokenID, bio);
    }

    function batchSetNameAndBio(
        bytes32[] memory _names,
        string[] memory _bios,
        uint256[] memory tokenIDs
    ) external payable override nonReentrant {
        require(
            _names.length == _bios.length,
            "KongNaming::different length names and bios"
        );
        require(
            _bios.length == tokenIDs.length,
            "KongNaming::different length bios and tokenIDs"
        );
        bool ownerOfAllKongs = isOwnerOfKongs(tokenIDs);
        require(
            msg.sender == admin || ownerOfAllKongs,
            "KongNaming::not authorized"
        );

        uint256 payableSets = 0;

        for (uint256 i = 0; i < _names.length; i++) {
            if (bioWasSet[tokenIDs[i]] == false) {
                bios[tokenIDs[i]] = _bios[i];
                bioWasSet[tokenIDs[i]] = true;
            } else {
                bios[tokenIDs[i]] = _bios[i];
                payableSets += 1;
            }

            if (nameWasSet[tokenIDs[i]] == false) {
                names[tokenIDs[i]] = _names[i];
                nameWasSet[tokenIDs[i]] = true;
            } else {
                names[tokenIDs[i]] = _names[i];
                payableSets += 1;
            }

            emit IKongNaming.SetName(tokenIDs[i], _names[i]);
            emit IKongNaming.SetBio(tokenIDs[i], _bios[i]);
        }

        if (ownerOfAllKongs) {
            require(
                msg.value == payableSets * changePrice,
                "KongNaming::insufficient ether sent"
            );
        }
    }

    function isOwnerOfKong(uint256 tokenID) private view returns (bool) {
        address ownerOfKong = rkl.ownerOf(tokenID);
        return msg.sender == ownerOfKong;
    }

    function isOwnerOfKongs(uint256[] memory tokenIDs)
        private
        view
        returns (bool)
    {
        for (uint256 i = 0; i < tokenIDs.length; i++) {
            if (msg.sender != rkl.ownerOf(tokenIDs[i])) {
                return false;
            }
        }
        return true;
    }

    function ensureAddressNotZero(address checkThis) private pure {
        require(checkThis != address(0), "KongNaming::address is zero");
    }

    function editPrice(uint256 newChangePrice) external {
        require(msg.sender == admin, "KongNaming::unauthorized");
        changePrice = newChangePrice;
    }

    function withdraw() external {
        require(msg.sender == admin, "KongNaming::unauthorized");
        uint256 balance = address(this).balance;
        beneficiary.transfer(balance);
    }
}
