# standard imports
import os

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.address import to_checksum_address

# local imports
from eth_erc721 import EIP712Domain


class TestERC712(EthTesterCase):

    def setUp(self):
        address = os.urandom(20).hex()
        salt = os.urandom(32).hex()
        self.struct = EIP712Domain(
                name='Ether Mail',
                version='1',
                chain_id=42,
                verifying_contract=to_checksum_address('0xcccccccccccccccccccccccccccccccccccccccc'),
                salt=salt,
                )
