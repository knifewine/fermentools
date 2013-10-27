#!/bin/bash

SAVEIFS=$IFS
IFS=_

# use separator magic combined with set to split the zenity output into shell vars
set $(zenity --forms --separator=_ --add-entry="original gravity?"\
				   --add-entry="final gravity?")

OG=$1
FG=$2

abv_calculation=$(echo "scale=5; ((76.08)*($OG-$FG)/(1.775-$OG))*($FG/0.794)" | bc -l)
echo "original gravity: ${OG}"
echo "final gravity:    ${FG}"
echo "=  ${abv_calculation}% ABV"

# RESTORE IFS
IFS=$SAVEIFS
