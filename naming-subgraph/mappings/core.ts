import { BigInt } from "@graphprotocol/graph-ts";
import {
  SetName,
  SetBio
} from "../generated/KongNaming/KongNaming";
import { Kong, Name, Bio } from "../generated/schema";

function fetchKong(tokenID: BigInt): Kong {
  let kong = Kong.load(tokenID.toString());
  if (kong == null) {
    kong = new Kong(tokenID.toString());
    kong.save()
  }
  return <Kong>kong;
}

export function handleSetName(event: SetName): void {
  let params = event.params;

  let name = new Name(
    event.transaction.hash
      .toHexString()
      .concat("::")
      .concat(event.logIndex.toString())
  );

  let kong = fetchKong(params.tokenID);

  name.value = params.name.toString();
  name.kong = kong.id;

  name.save();
}

export function handleSetBio(event: SetBio): void {
  let params = event.params;

  let bio = new Bio(
    event.transaction.hash
      .toHexString()
      .concat("::")
      .concat(event.logIndex.toString())
  );

  let kong = fetchKong(params.tokenID);

  bio.value = params.bio;
  bio.kong = kong.id;

  bio.save();
}
