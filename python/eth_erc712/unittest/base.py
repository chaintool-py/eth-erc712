# standard imports
import os
import logging

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.address import to_checksum_address
from chainlib.connection import RPCConnection
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.gas import OverrideGasOracle
from chainlib.eth.gas import Gas
from chainlib.eth.tx import receipt

# local imports
from eth_erc712 import EIP712Domain

script_dir = os.path.realpath(os.path.dirname(__file__))
data_dir = os.path.join(script_dir, '..', 'data')

logg = logging.getLogger(__name__)


class TestERC712(EthTesterCase):

    def setUp(self):
        super(TestERC712, self).setUp()
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        gas_oracle = OverrideGasOracle(limit=1000000)
        fp = os.path.join(data_dir, 'ERC712Example.bin')
        f = open(fp, 'r')
        bytecode = f.read()
        f.close()
        c = Gas(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        (tx_hash, o) = c.create(self.accounts[0], None, 0, data=bytecode)
        r = self.conn.do(o)
        o = receipt(r)
        r = self.conn.do(o)
        self.address = to_checksum_address(r['contract_address'])
        logg.debug('erc712 example smart contract published with hash {} address {}'.format(r, self.address))

        address = os.urandom(20).hex()
        salt = os.urandom(32).hex()
        self.domain = EIP712Domain(
                name='Ether Mail',
                version='1',
                chain_id=42,
                verifying_contract=to_checksum_address('0xcccccccccccccccccccccccccccccccccccccccc'),
                salt=salt,
                )
