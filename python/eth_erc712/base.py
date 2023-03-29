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
        self.encode = self.get_contents


    def add(self, k, t, v):
        typ_checked = ABIContractType(t.value) 
        self.typ_literal(t.value + ' ' + k)
        m = getattr(self, t.value)
        m(v)


    def string(self, s):
        v = keccak256_string_to_hex(s)
        self.contents.append(v)
        self.add_type(ABIContractType.STRING)
        self.__log_latest_erc712(s)


    def bytes(self, s):
        v = keccak256_string_to_hex(s)
        self.contents.append(v)
        self.add_type(ABIContractType.BYTES)
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
        return self.encode_type() + self.encode_data()


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


    def get_contents(self):
        v = self.encode_type() + self.encode_data()
        r = keccak256(v)
        logg.debug('domainseparator material {} -> {}'.format(v.hex(), r.hex()))
        return r


class EIP712DomainEncoder(ERC712Encoder):
    
    def __init__(self, struct_name, domain):
        assert domain.__class__.__name__ == 'EIP712Domain'
        self.domain = domain
        self.__cache_data = b''
        super(EIP712DomainEncoder, self).__init__(struct_name)


    def __cache(self):
        if not self.dirty:
            return
        domain = self.domain.get_contents()
        contents = super(EIP712DomainEncoder, self).get_contents()
        self.__cache_data = domain + contents


    def get_contents(self):
        self.__cache()
        return self.__cache_data


    def get_domain(self):
        self.__cache()
        return self.__cache_data[:32]


    def get_type_hash(self):
        self.__cache()
        return self.__cache_data[32:64]


    def get_typed_data(self):
        self.__cache()
        return self.__cache_data[64:]


    def get_hash(self):
        return keccak256(self.get_type_hash() + self.get_typed_data())


    def __str__(self):
        self.__cache()
        domain = self.get_domain()
        data_hash = self.get_type_hash()
        data = self.get_typed_data()
        s = 'erc712domain\t{}\nerc712type\t{}\nerc712data\n'.format(
                domain.hex(),
                data_hash.hex(),
                )
        for i in range(0, len(data), 32):
            s += '\t' + data[i:i+32].hex() + '\n'

        return s
