# standard imports
import logging
import sha3

# external imports
from chainlib.eth.contract import ABIContractType
from chainlib.eth.contract import ABIContractEncoder
from chainlib.hash import keccak256
from chainlib.hash import keccak256_string_to_hex

logg = logging.getLogger(__name__)


class ERC712Encoder(ABIContractEncoder):

    def __init__(self, struct_name):
        super(ERC712Encoder, self).__init__()
        self.method(struct_name)
        self.ks = []
        self.encode = self.get_contents


    def add(self, k, t, v):
        typ_checked = ABIContractType(t.value) 
        self.typ_literal(t.value + ' ' + k)
        m = getattr(self, t.value)
        m(v)


    def string(self, s):
        self.types.append(ABIContractType.STRING)
        v = keccak256_string_to_hex(s)
        self.contents.append(v)
        self.__log_latest_erc712(s)


    def bytes(self, s):
        self.types.append(ABIContractType.BYTES)
        v = keccak256_string_to_hex(s)
        self.contents.append(v)
        self.__log_latest_erc712(s)


    def __log_latest_erc712(self, v):
        l = len(self.types) - 1 
        logg.debug('Encoder added {} -> {} ({})'.format(v, self.contents[l], self.types[l].value))


    def encode_type(self):
        v = self.get_method()
        r = keccak256(v)
        logg.debug('typehash material {} -> {}'.format(v, r.hex()))
        return r


    def encode_data(self):
        return b''.join(list(map(lambda x: bytes.fromhex(x), self.contents)))


    def get_contents(self):
        return b'\x19\x01' + self.encode_type() + self.encode_data()


class EIP712Domain(ERC712Encoder):

    def __init__(self, name=None, version=None, chain_id=None, verifying_contract=None, salt=None):
        super(EIP712Domain, self).__init__('EIP712Domain')
        if name != None:
            self.add('name', ABIContractType.STRING, name)
        if version != None:
            self.add('version', ABIContractType.STRING, version)
        if chain_id != None:
            self.add('chainId', ABIContractType.UINT256, chain_id)
        if verifying_contract != None:
            self.add('verifyingContract', ABIContractType.ADDRESS, verifying_contract)
        if salt != None:
            self.add('salt', ABIContractType.BYTES32, salt)
