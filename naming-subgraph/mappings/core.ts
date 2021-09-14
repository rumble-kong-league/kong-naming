import {
  SetName,
  SetBio
} from "../generated/KongNaming/KongNaming";
import { Kong, Name, Bio } from "../generated/schema";

function fetchKong(): Kong { }

export function handleSetName(event: SetName): void {
  let params = event.params;

  let name = new Name(
    event.transaction.hash
      .toString()
      .concat("::")
      .concat(event.logIndex.toString())
  );

  let kong = fetchKong();

  name.value = params.name.toString();
  name.kong = kong.id;

  name.save();
}

export function handleSetBio(event: SetBio): void {
  let params = event.params;

  let bio = new Bio(
    event.transaction.hash
      .toString()
      .concat("::")
      .concat(event.logIndex.toString())
  );

  let kong = fetchKong();

  bio.value = params.bio;
  bio.kong = kong.id;

  bio.save();
}
