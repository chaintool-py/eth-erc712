# standard imports
import unittest
import logging
import os

# external imports
from chainlib.eth.contract import ABIContractType

# local imports
from eth_erc721.unittest import TestERC712 as TestERC712Base
from eth_erc721 import ERC712Encoder

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class ExamplePerson(ERC712Encoder):

    def __init__(self, name, wallet):
        super(ExamplePerson, self).__init__('Person')
        self.add('name', ABIContractType.STRING, name)
        self.add('wallet', ABIContractType.ADDRESS, wallet)


class ExampleMail(ERC712Encoder):

    def __init__(self, from_name, from_wallet, to_name, to_wallet, contents):
        self.pfrom = ExamplePerson(from_name, from_wallet)
        self.pto = ExamplePerson(to_name, to_wallet)
        super(ExampleMail, self).__init__('Mail')
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
        r = self.struct.encode_type()
        self.assertEqual(r, bytes.fromhex('d87cd6ef79d4e2b95e15ce8abf732db51ec771f1ca2edccf22a46c729ac56472'))


    def test_domain_data(self):
        r = self.struct.get()
        print(r.hex())


    def test_mail(self):
        a = os.urandom(20).hex()
        b = os.urandom(20).hex()
        o = ExampleMail('Pinky Inky', a, 'Clyde Blinky', b, 'barbarbar')
        r = o.get()
        print(r.hex())


if __name__ == '__main__':
    unittest.main()
