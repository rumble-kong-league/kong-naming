from brownie import E721, KongNaming, accounts
from brownie.network.gas.strategies import GasNowStrategy
from brownie.network import gas_price

gas_strategy = GasNowStrategy("fast")
gas_price(gas_strategy)

def main():
  acc = accounts.load("algo_two")
  rkl = E721.deploy({'from': acc})
  kong_naming = KongNaming.deploy(acc, acc, rkl.address, {'from': acc})
