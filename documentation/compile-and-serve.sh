#!/bin/bash

make html

if command -v entr >/dev/null 2>&1
then
	ls conf.py *.rst | entr -pcs "make html" &
fi

cd ../documentation-build/html && python -m http.server 

pkill -P $$
wait
