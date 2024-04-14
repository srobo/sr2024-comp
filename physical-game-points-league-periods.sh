#!/bin/bash

cd $(dirname $0)

./plot-periods.py --output game-points-by-period --periods 1 2 3 4
