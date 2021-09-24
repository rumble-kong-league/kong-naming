// SPDX-License-Identifier: MIT
pragma solidity =0.8.7;

import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/security/ReentrancyGuard.sol";

import "../interfaces/IKongNaming.sol";
import "../interfaces/IERC721.sol";

contract KongNaming is IKongNaming, ReentrancyGuard {
    mapping(uint256 => bytes32) public names;
    mapping(uint256 => string) public bios;

    mapping(uint256 => bool) private nameWasSet;
    mapping(uint256 => bool) private bioWasSet;

    IERC721 public immutable rkl;
    address public admin;
    address payable public beneficiary;
    uint256 public changePrice = 0.025 ether;

    constructor(
        address newAdmin,
        address payable newBeneficiary,
        address newRkl
    ) {
        ensureAddressNotZero(newAdmin);
        ensureAddressNotZero(newBeneficiary);
        ensureAddressNotZero(newRkl);
        rkl = IERC721(newRkl);
        admin = newAdmin;
        beneficiary = newBeneficiary;
    }

    function setName(bytes32 name, uint256 tokenID)
        external
        payable
        override
        nonReentrant
    {
        // check that the caller is either an owner or admin
        bool isOwner = isOwnerOfKong(tokenID);
        require(msg.sender == admin || isOwner, "KongNaming::unauthorized");

        // if this is the first time the name is set, mark that the
        // next time won't be and set the name
        if (nameWasSet[tokenID] == false) {
            nameWasSet[tokenID] = true;
        } else {
            // if it was the owner that called the function, require
            // the payment
            if (isOwner) {
                require(
                    msg.value == changePrice,
                    "KongNaming::insufficient ether sent"
                );
            }
        }

        names[tokenID] = name;
        emit IKongNaming.SetName(tokenID, name);
    }

    function setBio(string memory bio, uint256 tokenID)
        external
        payable
        override
        nonReentrant
    {
        // check that the caller is either an owner or admin
        bool isOwner = isOwnerOfKong(tokenID);
        require(msg.sender == admin || isOwner, "KongNaming::unauthorized");

        // if this is the first time the bio is set, mark that the
        // next time won't be and set the bio
        if (bioWasSet[tokenID] == false) {
            bioWasSet[tokenID] = true;
        } else {
            // if it was the owner that called the function, require
            // the payment
            if (isOwner) {
                require(
                    msg.value == changePrice,
                    "KongNaming::insufficient ether sent"
                );
            }
        }

        bios[tokenID] = bio;
        emit IKongNaming.SetBio(tokenID, bio);
    }

    function setNameAndBio(
        bytes32 name,
        string memory bio,
        uint256 tokenID
    ) external payable override nonReentrant {
        uint256 payableSets = 0;

        bool isOwner = isOwnerOfKong(tokenID);
        require(msg.sender == admin || isOwner, "KongNaming::unauthorized");

        if (bioWasSet[tokenID] == false) {
            bioWasSet[tokenID] = true;
        } else {
            payableSets += 1;
        }

        if (nameWasSet[tokenID] == false) {
            nameWasSet[tokenID] = true;
        } else {
            payableSets += 1;
        }

        if (isOwner) {
            require(
                msg.value == payableSets * changePrice,
                "KongNaming::insufficient ether sent"
            );
        }

        names[tokenID] = name;
        bios[tokenID] = bio;
        emit IKongNaming.SetName(tokenID, name);
        emit IKongNaming.SetBio(tokenID, bio);
    }

    function batchSetName(bytes32[] memory _names, uint256[] memory tokenIDs)
        external
        payable
        override
        nonReentrant
    {
        // sanity checks
        require(
            _names.length == tokenIDs.length,
            "KongNaming::different length names and tokenIDs"
        );
        // returns true if the sender is owner of all the passed tokenIDs
        bool ownerOfAllKongs = isOwnerOfKongs(tokenIDs);
        // require the caller to be the owner of all of the tokenIDs or be
        // an admin
        require(
            msg.sender == admin || ownerOfAllKongs,
            "KongNaming::unauthorized"
        );

        // counter to check how much ether should be sent
        uint256 payableSets = 0;

        for (uint256 i = 0; i < _names.length; i) {
            if (nameWasSet[tokenIDs[i]] == false) {
                nameWasSet[tokenIDs[i]] = true;
            } else {
                payableSets += 1;
            }

            names[tokenIDs[i]] = _names[i];
            emit IKongNaming.SetName(tokenIDs[i], _names[i]);
        }

        // if it is owner who called, ensure that they have sent adequate
        // payment
        if (ownerOfAllKongs) {
            require(
                msg.value == payableSets * changePrice,
                "KongNaming::insufficient ether sent"
            );
        }
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
                bioWasSet[tokenIDs[i]] = true;
            } else {
                payableSets += 1;
            }

            bios[tokenIDs[i]] = _bios[i];
            emit IKongNaming.SetBio(tokenIDs[i], _bios[i]);
        }

        if (ownerOfAllKongs) {
            require(
                msg.value == payableSets * changePrice,
                "KongNaming::insufficient ether sent"
            );
        }
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
                bioWasSet[tokenIDs[i]] = true;
            } else {
                payableSets += 1;
            }
            if (nameWasSet[tokenIDs[i]] == false) {
                nameWasSet[tokenIDs[i]] = true;
            } else {
                payableSets += 1;
            }

            names[tokenIDs[i]] = _names[i];
            bios[tokenIDs[i]] = _bios[i];
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
        return msg.sender == rkl.ownerOf(tokenID);
    }

    function isOwnerOfKongs(uint256[] memory tokenIDs)
        private
        view
        returns (bool)
    {
        for (uint256 i = 0; i < tokenIDs.length; i++) {
            if (!isOwnerOfKong(tokenIDs[i])) {
                return false;
            }
        }
        return true;
    }

    function ensureAddressNotZero(address checkThisAddress) private pure {
        require(checkThisAddress != address(0), "KongNaming::address is zero");
    }

    function editPrice(uint256 newChangePrice) external {
        require(msg.sender == admin, "KongNaming::unauthorized");
        changePrice = newChangePrice;
    }

    function editBeneficiary(address payable newBeneficiary) external {
        require(msg.sender == admin, "KongNaming::unauthorized");
        beneficiary = newBeneficiary;
    }

    function editAdmin(address newAdmin) external {
        require(msg.sender == admin, "KongNaming::unauthorized");
        admin = newAdmin;
    }

    function withdraw() external {
        require(msg.sender == admin, "KongNaming::unauthorized");
        beneficiary.transfer(address(this).balance);
    }
}
