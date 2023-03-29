#!/bin/bash

export PYTHONPATH=${PYTHONPATH}:.
>&2 echo "using pythonpath $PYTHONPATH"

set -e
set -x
for f in `ls tests/*.py`; do
	python $f
	if [ $? -gt 0 ]; then
		exit 1
	fi
done
set +x
set +e
