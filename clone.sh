#!/bin/sh
# Fetch the corpora this analysis reads. Mathlib is not cloned: the scripts
# read an existing checkout, passed as an argument to import_graph.py.
set -e
mkdir -p corpora
cd corpora
[ -d TauCeti ] || git clone https://github.com/TauCetiProject/TauCeti.git TauCeti
[ -d merely-true ] || git clone --depth 1 https://github.com/merely-true/merely-true.git merely-true
