# standard imports
import unittest
import logging
import os

# external imports
from chainlib.eth.contract import ABIContractType
from chainlib.eth.tx import TxFactory
from chainlib.eth.tx import TxFormat
from chainlib.jsonrpc import JSONRPCRequest
from chainlib.eth.contract import ABIContractEncoder
from chainlib.eth.contract import ABIContractType
from hexathon import add_0x

# local imports
from eth_erc712.unittest import TestERC712 as TestERC712Base
from eth_erc712 import ERC712Encoder
from eth_erc712 import EIP712DomainEncoder

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class ExamplePerson(ERC712Encoder):

    def __init__(self, name, wallet):
        super(ExamplePerson, self).__init__('Person')
        self.add('name', ABIContractType.STRING, name)
        self.add('wallet', ABIContractType.ADDRESS, wallet)


class ExampleMail(EIP712DomainEncoder):
    def __init__(self, from_name, from_wallet, to_name, to_wallet, contents, *args, **kwargs):
        self.pfrom = ExamplePerson(from_name, from_wallet)
        self.pto = ExamplePerson(to_name, to_wallet)
        super(ExampleMail, self).__init__('Mail', *args, **kwargs)
        self.typ_literal('Person from')
        self.typ_literal('Person to')
        self.add('contents', ABIContractType.STRING, contents)


    # In general implementation, remember to sort structs alphabetically
    def get_method(self):
        typ = super(ExampleMail, self).get_method()
        typ += self.pto.get_method()
        logg.debug('Method is composite type: ' + typ)
        return typ


    def encode_data(self):
        content = super(ExampleMail, self).encode_data()
        from_content = self.pfrom.encode_data()
        to_content = self.pto.encode_data()
        return from_content + to_content + content


class TestERC712(TestERC712Base):

    def test_domain_separator(self):
        r = self.domain.encode_type()
        self.assertEqual(r, bytes.fromhex('d87cd6ef79d4e2b95e15ce8abf732db51ec771f1ca2edccf22a46c729ac56472'))


    def test_domain_data(self):
        r = self.domain.get()
        print(r.hex())


    def test_mail(self):
        a = os.urandom(20).hex()
        b = os.urandom(20).hex()
        mail = ExampleMail('Pinky Inky', a, 'Clyde Blinky', b, 'barbarbar', domain=self.domain)
        sig = self.signer.sign_typed_message(self.accounts[0], mail.get_domain(), mail.get_data_hash())
        sig = sig[:64] + (sig[64] + 27).to_bytes(1, byteorder='big')
        logg.debug('message is:\n{}\nsigned by {}'.format(mail, self.accounts[0]))

        c = TxFactory(self.chain_spec)
        j = JSONRPCRequest()
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('verify')
        enc.typ_literal('Mail')
        enc.typ(ABIContractType.UINT8)
        enc.typ(ABIContractType.BYTES32)
        enc.typ(ABIContractType.BYTES32)
        enc.bytes(mail.get_typed_data().hex())
        enc.uintn(sig[64], 8)
        enc.bytes32(sig[:32])
        enc.bytes32(sig[32:64])
        data = add_0x(enc.get())
        tx = c.template(self.accounts[0], self.address)
        tx = c.set_code(tx, data)
        o['params'].append(c.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        r = self.rpc.do(o)
        r = strip_0x(r)
        self.assertEqual(int(r, 16), 1)


if __name__ == '__main__':
    unittest.main()
