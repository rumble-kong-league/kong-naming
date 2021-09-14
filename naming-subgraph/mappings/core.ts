import { BigInt, store } from "@graphprotocol/graph-ts";
import {
  Lent,
  Rented,
  Returned,
  CollateralClaimed,
  LendingStopped,
} from "../generated/ReNFT/ReNFT";
import { Lending, Renting, Nft, User, LendingRentingCount } from "../generated/schema";
import { fetchUser, fetchNft, getNftId } from "./helpers";

// TODO: placeholder

export function handleLent(event: Lent): void {
  let lentParams = event.params;
  // imagine the following: contract A & contract B
  // contract A is the owner of the NFT
  // they lend it out. They don't see it in their Lend tab
  // contract B borrows. Now they can lend it out
  // they lend it out, and now contrct A can see it and rent it out
  // if contract A defaults, they will pay the collateral
  // this will trigger contract B default, which means contract
  // A can now claim the collateral
  // For this reason the NFT id must have additional information
  // this means that the same actual NFT may have more than one
  // entry in the graph. Number of entries is determined by how
  // many times it was lent out. The so-called NFT "hot-potato"
  // AKA mortgage backed security

  let lending = new Lending(lentParams.lendingId.toString());

  lending.nftAddress = lentParams.nftAddress;
  lending.tokenId = lentParams.tokenId;
  lending.lenderAddress = lentParams.lenderAddress;
  lending.maxRentDuration = BigInt.fromI32(lentParams.maxRentDuration);
  lending.dailyRentPrice = lentParams.dailyRentPrice;
  lending.nftPrice = lentParams.nftPrice;
  lending.paymentToken = BigInt.fromI32(lentParams.paymentToken);
  lending.collateralClaimed = false;
  lending.lentAmount = BigInt.fromI32(lentParams.lentAmount);
  lending.isERC721 = lentParams.isERC721;

  let lender = fetchUser(lentParams.lenderAddress);
  lending.lenderUser = lender.id;

  let nftId = getNftId(lending.nftAddress, lending.tokenId, lending.lentAmount);
  let nft = fetchNft(nftId);
  lending.nft = nft.id;

  lrc.lending = lrc.lending.plus(BigInt.fromI32(1));

  lending.save();
  lender.save();
  nft.save();
  lrc.save();
}

export function handleRented(event: Rented): void {
  let rentedParams = event.params;
  let lendingId = rentedParams.lendingId.toString();

  let renting = new Renting(lendingId);
  renting.renterAddress = rentedParams.renterAddress;
  renting.rentDuration = BigInt.fromI32(rentedParams.rentDuration);
  renting.rentedAt = rentedParams.rentedAt;
  renting.lending = lendingId;

  let renter = fetchUser(rentedParams.renterAddress);
  renting.renterUser = renter.id;

  let lending = Lending.load(lendingId);
  lending.renting = renting.id;
  let nftId = getNftId(lending.nftAddress, lending.tokenId, lending.lentAmount);
  // we know nft exists here, no need to fetch
  let nft = Nft.load(nftId);
  renting.nft = nft.id;

  lrc.renting = lrc.renting.plus(BigInt.fromI32(1));

  lending.save();
  renting.save();
  renter.save();
  nft.save();
  lrc.save();
}

// on returned, we remove renting from Nft
// we remove from User
// and we null out the renting field in Lending
export function handleReturned(event: Returned): void {
  let returnParams = event.params;
  let lending = Lending.load(returnParams.lendingId.toString());
  let renting = lending.renting;
  let Renter = Renting.load(renting);

  let renter = User.load(Renter.renterAddress.toHexString());
  store.remove("Renting", renting);

  let nftId = getNftId(lending.nftAddress, lending.tokenId, lending.lentAmount);
  let nft = Nft.load(nftId);

  lending.renting = null;

  lrc.renting = lrc.renting.minus(BigInt.fromI32(1));

  renter.save();
  lending.save();
  nft.save();
  lrc.save();
}

// on collateral claim we must remove the lending and renting from LendingRenting
// we must also remove this from the corresponding users' profiles
// renting
export function handleClaimCollateral(event: CollateralClaimed): void {
  let claimParams = event.params;
  let lending = Lending.load(claimParams.lendingId.toString());

  let nftId = getNftId(lending.nftAddress, lending.tokenId, lending.lentAmount);
  let nft = Nft.load(nftId);

  lending.collateralClaimed = true;

  lrc.renting = lrc.renting.minus(BigInt.fromI32(1));
  lrc.lending = lrc.lending.plus(BigInt.fromI32(1));

  lending.save();
  nft.save();
  lrc.save();
}

// when someone stops lending, we must remove the entity from the user's
// lending field
export function handleStopLending(event: LendingStopped): void {
  let lendingStopParams = event.params;
  let lending = Lending.load(lendingStopParams.lendingId.toString());

  lrc.lending = lrc.lending.plus(BigInt.fromI32(1));

  store.remove('Lending', lending.id);
  // it is incorrect to call save after store remove operation. the below will not work
  // lending.save();
  lrc.save();
}
