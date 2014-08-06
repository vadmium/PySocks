#!/bin/bash
export PYTHON2=python2
type "$PYTHON2" >/dev/null 2>&1 || PYTHON2=python

if test "$#" -eq 0; then
    set -- "$PYTHON2" python3
fi

./mocks start

for PYTHON; do
    echo "$PYTHON tests"
    "$PYTHON" sockstest.py -v
done

./mocks shutdown
echo "Finished tests"
