#!/bin/bash
export PYTHON2=python2
type "$PYTHON2" >/dev/null 2>&1 || PYTHON2=python

if test "$#" -eq 0; then
    set -- "$PYTHON2" python3
fi

echo "Starting proxy servers..."
python2 socks4server.py > /dev/null &
python2 httpproxy.py > /dev/null &
./mocks start

for PYTHON; do
    sleep 2
    echo "$PYTHON tests"
    "$PYTHON" sockstest.py -v
done

pkill python2 > /dev/null
./mocks shutdown
echo "Finished tests"
