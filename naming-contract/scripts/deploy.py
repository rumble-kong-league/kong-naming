from brownie import E721, KongNaming, accounts
from brownie.network.gas.strategies import GasNowStrategy
from brownie.network import gas_price

gas_strategy = GasNowStrategy("fast")
gas_price(gas_strategy)


def main():
    acc = accounts.load("algo_two")

    rkl_address = "0xef0182dc0574cd5874494a120750fd222fdb909a"
    treasury = "0x2B5964447005f661D13637CBDFFFCe600708138f"

    KongNaming.deploy(acc.address, treasury, rkl_address, {"from": acc})
