#!/bin/bash

SAVEIFS=$IFS
IFS=_

# use separator magic combined with set to split the zenity output into shell vars
set $(\
 zenity --forms --separator=_ --add-entry="how many gallons into kettle?"\
  --add-entry="how many pounds of grain to mash?"\
  --add-entry="quarts/lb ratio?"\
  --add-entry="initial grain temp (F)?"\
  --add-entry="target mash temp (F)?"\
  --add-entry="target sparge (rinse) temp?")

gallons=$1
lb_grain=$2
q_lb_ratio=$3
grain_temp=$4
target_temp=$5
target_sparge_temp=$6

# this will vary from .1 to maybe .2 depending on the crush
grain_absorption=0.15
gal_per_quart=0.25


strike_gal=$(echo "scale=3; ($lb_grain*$q_lb_ratio*$gal_per_quart)" | bc -l)
strike_temp=$(echo "scale=3; (0.2/$q_lb_ratio)*($target_temp-$grain_temp)+($target_temp)" | bc -l)
water_absorbed=$(echo "scale=3; $lb_grain*$grain_absorption" | bc -l)
runnings=$(echo "scale=3; $strike_gal - $water_absorbed" | bc -l)

echo
echo "STRIKE with ${strike_gal} gallons of water at ${strike_temp} degrees to collect ${runnings} gallons of wort"

# water into sparge should equal runnings out
sparge_water_gal=$(echo "scale=3; $gallons - $runnings" | bc -l)
sparge_runnings=$sparge_water_gal
# TODO: recalculate the q_lb_ratio based on how much weight in runnings have been collected during strike?
# TODO: I don't think below is the correct formula for figuring out how to raise the mash bed to the sparge temp
sparge_water_temp=$(echo "scale=3; (0.2/$q_lb_ratio)*($target_sparge_temp-$target_temp)+($target_sparge_temp)" | bc -l)

#our total_wort should equal approx gallons into kettle
total_wort=$(echo "scale=3; $runnings+$sparge_runnings" | bc -l)

echo
echo "SPARGE with ${sparge_water_gal} of water at ${sparge_water_temp} to collect ${sparge_runnings} of wort"
echo

echo "details:"
echo " + ${strike_gal} gallons of water into mash tun at ${strike_temp} degrees"
echo " - ${water_absorbed} gallons absorbed by grain"
echo " + ${sparge_runnings} gallons of water to sparge at ${sparge_water_temp} degrees"
echo "-----------------------------------------------"
echo " = ${total_wort} gallons of wort collected"


# RESTORE IFS
IFS=$SAVEIFS
