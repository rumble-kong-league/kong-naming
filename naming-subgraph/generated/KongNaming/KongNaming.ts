// THIS IS AN AUTOGENERATED FILE. DO NOT EDIT THIS FILE DIRECTLY.

import {
  ethereum,
  JSONValue,
  TypedMap,
  Entity,
  Bytes,
  Address,
  BigInt
} from "@graphprotocol/graph-ts";

export class SetBio extends ethereum.Event {
  get params(): SetBio__Params {
    return new SetBio__Params(this);
  }
}

export class SetBio__Params {
  _event: SetBio;

  constructor(event: SetBio) {
    this._event = event;
  }

  get tokenID(): BigInt {
    return this._event.parameters[0].value.toBigInt();
  }

  get bio(): string {
    return this._event.parameters[1].value.toString();
  }
}

export class SetName extends ethereum.Event {
  get params(): SetName__Params {
    return new SetName__Params(this);
  }
}

export class SetName__Params {
  _event: SetName;

  constructor(event: SetName) {
    this._event = event;
  }

  get tokenID(): BigInt {
    return this._event.parameters[0].value.toBigInt();
  }

  get name(): Bytes {
    return this._event.parameters[1].value.toBytes();
  }
}

export class KongNaming extends ethereum.SmartContract {
  static bind(address: Address): KongNaming {
    return new KongNaming("KongNaming", address);
  }

  admin(): Address {
    let result = super.call("admin", "admin():(address)", []);

    return result[0].toAddress();
  }

  try_admin(): ethereum.CallResult<Address> {
    let result = super.tryCall("admin", "admin():(address)", []);
    if (result.reverted) {
      return new ethereum.CallResult();
    }
    let value = result.value;
    return ethereum.CallResult.fromValue(value[0].toAddress());
  }

  beneficiary(): Address {
    let result = super.call("beneficiary", "beneficiary():(address)", []);

    return result[0].toAddress();
  }

  try_beneficiary(): ethereum.CallResult<Address> {
    let result = super.tryCall("beneficiary", "beneficiary():(address)", []);
    if (result.reverted) {
      return new ethereum.CallResult();
    }
    let value = result.value;
    return ethereum.CallResult.fromValue(value[0].toAddress());
  }

  bios(param0: BigInt): string {
    let result = super.call("bios", "bios(uint256):(string)", [
      ethereum.Value.fromUnsignedBigInt(param0)
    ]);

    return result[0].toString();
  }

  try_bios(param0: BigInt): ethereum.CallResult<string> {
    let result = super.tryCall("bios", "bios(uint256):(string)", [
      ethereum.Value.fromUnsignedBigInt(param0)
    ]);
    if (result.reverted) {
      return new ethereum.CallResult();
    }
    let value = result.value;
    return ethereum.CallResult.fromValue(value[0].toString());
  }

  changePrice(): BigInt {
    let result = super.call("changePrice", "changePrice():(uint256)", []);

    return result[0].toBigInt();
  }

  try_changePrice(): ethereum.CallResult<BigInt> {
    let result = super.tryCall("changePrice", "changePrice():(uint256)", []);
    if (result.reverted) {
      return new ethereum.CallResult();
    }
    let value = result.value;
    return ethereum.CallResult.fromValue(value[0].toBigInt());
  }

  names(param0: BigInt): Bytes {
    let result = super.call("names", "names(uint256):(bytes32)", [
      ethereum.Value.fromUnsignedBigInt(param0)
    ]);

    return result[0].toBytes();
  }

  try_names(param0: BigInt): ethereum.CallResult<Bytes> {
    let result = super.tryCall("names", "names(uint256):(bytes32)", [
      ethereum.Value.fromUnsignedBigInt(param0)
    ]);
    if (result.reverted) {
      return new ethereum.CallResult();
    }
    let value = result.value;
    return ethereum.CallResult.fromValue(value[0].toBytes());
  }

  rkl(): Address {
    let result = super.call("rkl", "rkl():(address)", []);

    return result[0].toAddress();
  }

  try_rkl(): ethereum.CallResult<Address> {
    let result = super.tryCall("rkl", "rkl():(address)", []);
    if (result.reverted) {
      return new ethereum.CallResult();
    }
    let value = result.value;
    return ethereum.CallResult.fromValue(value[0].toAddress());
  }
}

export class ConstructorCall extends ethereum.Call {
  get inputs(): ConstructorCall__Inputs {
    return new ConstructorCall__Inputs(this);
  }

  get outputs(): ConstructorCall__Outputs {
    return new ConstructorCall__Outputs(this);
  }
}

export class ConstructorCall__Inputs {
  _call: ConstructorCall;

  constructor(call: ConstructorCall) {
    this._call = call;
  }

  get newAdmin(): Address {
    return this._call.inputValues[0].value.toAddress();
  }

  get newBeneficiary(): Address {
    return this._call.inputValues[1].value.toAddress();
  }

  get newRkl(): Address {
    return this._call.inputValues[2].value.toAddress();
  }
}

export class ConstructorCall__Outputs {
  _call: ConstructorCall;

  constructor(call: ConstructorCall) {
    this._call = call;
  }
}

export class BatchSetBioCall extends ethereum.Call {
  get inputs(): BatchSetBioCall__Inputs {
    return new BatchSetBioCall__Inputs(this);
  }

  get outputs(): BatchSetBioCall__Outputs {
    return new BatchSetBioCall__Outputs(this);
  }
}

export class BatchSetBioCall__Inputs {
  _call: BatchSetBioCall;

  constructor(call: BatchSetBioCall) {
    this._call = call;
  }

  get _bios(): Array<string> {
    return this._call.inputValues[0].value.toStringArray();
  }

  get tokenIDs(): Array<BigInt> {
    return this._call.inputValues[1].value.toBigIntArray();
  }
}

export class BatchSetBioCall__Outputs {
  _call: BatchSetBioCall;

  constructor(call: BatchSetBioCall) {
    this._call = call;
  }
}

export class BatchSetNameCall extends ethereum.Call {
  get inputs(): BatchSetNameCall__Inputs {
    return new BatchSetNameCall__Inputs(this);
  }

  get outputs(): BatchSetNameCall__Outputs {
    return new BatchSetNameCall__Outputs(this);
  }
}

export class BatchSetNameCall__Inputs {
  _call: BatchSetNameCall;

  constructor(call: BatchSetNameCall) {
    this._call = call;
  }

  get _names(): Array<Bytes> {
    return this._call.inputValues[0].value.toBytesArray();
  }

  get tokenIDs(): Array<BigInt> {
    return this._call.inputValues[1].value.toBigIntArray();
  }
}

export class BatchSetNameCall__Outputs {
  _call: BatchSetNameCall;

  constructor(call: BatchSetNameCall) {
    this._call = call;
  }
}

export class BatchSetNameAndBioCall extends ethereum.Call {
  get inputs(): BatchSetNameAndBioCall__Inputs {
    return new BatchSetNameAndBioCall__Inputs(this);
  }

  get outputs(): BatchSetNameAndBioCall__Outputs {
    return new BatchSetNameAndBioCall__Outputs(this);
  }
}

export class BatchSetNameAndBioCall__Inputs {
  _call: BatchSetNameAndBioCall;

  constructor(call: BatchSetNameAndBioCall) {
    this._call = call;
  }

  get _names(): Array<Bytes> {
    return this._call.inputValues[0].value.toBytesArray();
  }

  get _bios(): Array<string> {
    return this._call.inputValues[1].value.toStringArray();
  }

  get tokenIDs(): Array<BigInt> {
    return this._call.inputValues[2].value.toBigIntArray();
  }
}

export class BatchSetNameAndBioCall__Outputs {
  _call: BatchSetNameAndBioCall;

  constructor(call: BatchSetNameAndBioCall) {
    this._call = call;
  }
}

export class EditAdminCall extends ethereum.Call {
  get inputs(): EditAdminCall__Inputs {
    return new EditAdminCall__Inputs(this);
  }

  get outputs(): EditAdminCall__Outputs {
    return new EditAdminCall__Outputs(this);
  }
}

export class EditAdminCall__Inputs {
  _call: EditAdminCall;

  constructor(call: EditAdminCall) {
    this._call = call;
  }

  get newAdmin(): Address {
    return this._call.inputValues[0].value.toAddress();
  }
}

export class EditAdminCall__Outputs {
  _call: EditAdminCall;

  constructor(call: EditAdminCall) {
    this._call = call;
  }
}

export class EditBeneficiaryCall extends ethereum.Call {
  get inputs(): EditBeneficiaryCall__Inputs {
    return new EditBeneficiaryCall__Inputs(this);
  }

  get outputs(): EditBeneficiaryCall__Outputs {
    return new EditBeneficiaryCall__Outputs(this);
  }
}

export class EditBeneficiaryCall__Inputs {
  _call: EditBeneficiaryCall;

  constructor(call: EditBeneficiaryCall) {
    this._call = call;
  }

  get newBeneficiary(): Address {
    return this._call.inputValues[0].value.toAddress();
  }
}

export class EditBeneficiaryCall__Outputs {
  _call: EditBeneficiaryCall;

  constructor(call: EditBeneficiaryCall) {
    this._call = call;
  }
}

export class EditPriceCall extends ethereum.Call {
  get inputs(): EditPriceCall__Inputs {
    return new EditPriceCall__Inputs(this);
  }

  get outputs(): EditPriceCall__Outputs {
    return new EditPriceCall__Outputs(this);
  }
}

export class EditPriceCall__Inputs {
  _call: EditPriceCall;

  constructor(call: EditPriceCall) {
    this._call = call;
  }

  get newChangePrice(): BigInt {
    return this._call.inputValues[0].value.toBigInt();
  }
}

export class EditPriceCall__Outputs {
  _call: EditPriceCall;

  constructor(call: EditPriceCall) {
    this._call = call;
  }
}

export class SetBioCall extends ethereum.Call {
  get inputs(): SetBioCall__Inputs {
    return new SetBioCall__Inputs(this);
  }

  get outputs(): SetBioCall__Outputs {
    return new SetBioCall__Outputs(this);
  }
}

export class SetBioCall__Inputs {
  _call: SetBioCall;

  constructor(call: SetBioCall) {
    this._call = call;
  }

  get bio(): string {
    return this._call.inputValues[0].value.toString();
  }

  get tokenID(): BigInt {
    return this._call.inputValues[1].value.toBigInt();
  }
}

export class SetBioCall__Outputs {
  _call: SetBioCall;

  constructor(call: SetBioCall) {
    this._call = call;
  }
}

export class SetNameCall extends ethereum.Call {
  get inputs(): SetNameCall__Inputs {
    return new SetNameCall__Inputs(this);
  }

  get outputs(): SetNameCall__Outputs {
    return new SetNameCall__Outputs(this);
  }
}

export class SetNameCall__Inputs {
  _call: SetNameCall;

  constructor(call: SetNameCall) {
    this._call = call;
  }

  get name(): Bytes {
    return this._call.inputValues[0].value.toBytes();
  }

  get tokenID(): BigInt {
    return this._call.inputValues[1].value.toBigInt();
  }
}

export class SetNameCall__Outputs {
  _call: SetNameCall;

  constructor(call: SetNameCall) {
    this._call = call;
  }
}

export class SetNameAndBioCall extends ethereum.Call {
  get inputs(): SetNameAndBioCall__Inputs {
    return new SetNameAndBioCall__Inputs(this);
  }

  get outputs(): SetNameAndBioCall__Outputs {
    return new SetNameAndBioCall__Outputs(this);
  }
}

export class SetNameAndBioCall__Inputs {
  _call: SetNameAndBioCall;

  constructor(call: SetNameAndBioCall) {
    this._call = call;
  }

  get name(): Bytes {
    return this._call.inputValues[0].value.toBytes();
  }

  get bio(): string {
    return this._call.inputValues[1].value.toString();
  }

  get tokenID(): BigInt {
    return this._call.inputValues[2].value.toBigInt();
  }
}

export class SetNameAndBioCall__Outputs {
  _call: SetNameAndBioCall;

  constructor(call: SetNameAndBioCall) {
    this._call = call;
  }
}

export class WithdrawCall extends ethereum.Call {
  get inputs(): WithdrawCall__Inputs {
    return new WithdrawCall__Inputs(this);
  }

  get outputs(): WithdrawCall__Outputs {
    return new WithdrawCall__Outputs(this);
  }
}

export class WithdrawCall__Inputs {
  _call: WithdrawCall;

  constructor(call: WithdrawCall) {
    this._call = call;
  }
}

export class WithdrawCall__Outputs {
  _call: WithdrawCall;

  constructor(call: WithdrawCall) {
    this._call = call;
  }
}
