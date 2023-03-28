SOLC = /usr/bin/solc

all:
	$(SOLC) --bin ERC712Example.sol --evm-version byzantium | awk 'NR>3' > ERC712Example.bin
	$(SOLC) --abi ERC712Example.sol --evm-version byzantium | awk 'NR>3' > ERC712Example.json
	$(SOLC) --metadata ERC712Example.sol --evm-version byzantium | awk 'NR>3' > ERC712Example.metadata.json
	truncate -s -1 ERC712Example.bin

install: all
	cp -v *.json ../python/eth_erc712/data/
	cp -v *.bin ../python/eth_erc712/data/

