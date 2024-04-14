#!/bin/bash

cd $(dirname $0)

./plot-game-points-by-match.py --start-match-num=21 --output physical-game-points-cumulative
