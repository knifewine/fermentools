fermentools
===========

various homebrewing-related python and bash travesties

mash_calc.py
------------
Basic Gtk mash calculator for English sparging. Constants are presently set in the source but should eventually
be pulled out as settings for varying parameters like grain absorption and specific heat of mash tun.

Requires python3 and gobject introspection libaries. Use a virtualenv and pip for your sanity.

mash_temp.sh
------------
Similar function to mash_calc.py but much less cool. Source code may encourage headaches, but it works.

Requires zenity but could easily be modified to take paramters directly from the command line if you have something against zenity.
Relies on some bash commands that you probably already have.

abv_calch.sh
------------
Simple, command-line abv calculator using the more complex calculation method which should yield more accurate calculations for higher gravity beers.

Requires zenity but could be easily modified to work without.
