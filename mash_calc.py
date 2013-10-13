#!/usr/bin/python3
from gi.repository import Gtk

WATER_LB_PER_GAL_AT_150F = 8.18
WATER_SPECIFIC_HEAT = 1
GRAIN_ABSORPTION_GAL_PER_LB = 0.14
GRAIN_SPECIFIC_HEAT = 0.38 # specific heat of grain, likely varies
MY_MASH_TUN_WEIGHT = 9.13 # lb, that is
MY_MASH_TUN_SPECIFIC_HEAT = 0.35 # specific heat of tun, varies depending on mash tun and materials


def round_num(num):
    """
    For consistent rounding behavior.
    """
    return round(num, 2)

def calculate_water_absorbed(lbs_grain):
    """
    Returns gallons absorbed by dry grain weight given.
    """
    return lbs_grain * GRAIN_ABSORPTION_GAL_PER_LB


def calculate_strike_temp(desired_temp, tun_temp, dry_grain_weight, grain_temp, gallons_water):
    """
    Returns the temperature of water required to make the mash finalize at desired_temp

    This is based on the fact that (according to thermodynamics):
    (M1)(C1)(T1) + (M2)(C2)(T2) = (M1*C1 + M2*C2) * TF

    Source: http://www.beersmith.com/Help/mashing_tech.htm
    """
    td = desired_temp

    m1 = MY_MASH_TUN_WEIGHT
    c1 = MY_MASH_TUN_SPECIFIC_HEAT
    t1 = tun_temp

    m2 = dry_grain_weight
    c2 = GRAIN_SPECIFIC_HEAT
    t2 = grain_temp

    m3 = gallons_water * WATER_LB_PER_GAL_AT_150F
    c3 = WATER_SPECIFIC_HEAT

    # because:
    #  m1*c1*t1 + m2*c2*t2 + m3*c3*t3 = desired_temp * (m1c1 + m2c2 + m3c3)
    # therefore, substituting the actual desired temp and solving for t3
    #  gives the formula below
    t3 = (td*m1*c1 + td*m2*c2 + td*m3*c3 - m1*c1*t1 - m2*c2*t2)/(m3*c3)

    return t3


def calculate_sparge_temp(desired_temp, settled_mash_temp, dry_grain_weight, gallons_water):
    td = desired_temp

    m1 = MY_MASH_TUN_WEIGHT
    c1 = MY_MASH_TUN_SPECIFIC_HEAT
    t1 = settled_mash_temp

    m2 = dry_grain_weight
    c2 = GRAIN_SPECIFIC_HEAT
    t2 = settled_mash_temp

    m3 = calculate_water_absorbed(dry_grain_weight) * WATER_LB_PER_GAL_AT_150F
    c3 = WATER_SPECIFIC_HEAT
    t3 = settled_mash_temp

    m4 = gallons_water * WATER_LB_PER_GAL_AT_150F
    c4 = WATER_SPECIFIC_HEAT
    t4 = (td*m1*c1 + td*m2*c2 + td*m3*c3 + td*m4*c4 - m1*c1*t1 - m2*c2*t2 - m3*c3*t3)/(m4*c4)

    return t4


class BatchSpageCalculatorWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Batch Sparge Calculator")
        self.set_border_width(15)

        self.gal_into_boil  = gal_into_boil = Gtk.SpinButton(digits=2, numeric=True)
        gal_into_boil.set_adjustment(Gtk.Adjustment(6, 0.25, 15, 0.25, 0.5, 0))
        gal_into_boil.connect("value-changed", self.recalculate)

        self.grain_bill_lb  = grain_bill_lb = Gtk.SpinButton(digits=2, numeric=True)
        grain_bill_lb.set_adjustment(Gtk.Adjustment(10, 0.25, 100, 0.25, 0.5, 0))
        grain_bill_lb.connect("value-changed", self.recalculate)

        self.grist_ratio = grist_ratio = Gtk.SpinButton(digits=2, numeric=True)
        grist_ratio.set_adjustment(Gtk.Adjustment(1.5, 0.25, 4, 0.25, 0.5, 0))
        grist_ratio.connect("value-changed", self.recalculate)

        self.initial_grain_temp = initial_grain_temp = Gtk.SpinButton(digits=2, numeric=True)
        initial_grain_temp.set_adjustment(Gtk.Adjustment(70, 0, 100, 0.5, 1, 0))
        initial_grain_temp.connect("value-changed", self.recalculate)

        self.empty_tun_temp = empty_tun_temp = Gtk.SpinButton(digits=2, numeric=True)
        empty_tun_temp.set_adjustment(Gtk.Adjustment(70, 0, 180, 0.5, 1, 0))
        empty_tun_temp.connect("value-changed", self.recalculate)

        self.target_mash_temp = target_mash_temp = Gtk.SpinButton(digits=2, numeric=True)
        target_mash_temp.set_adjustment(Gtk.Adjustment(152, 0, 180, 0.5, 1, 0))
        target_mash_temp.connect("value-changed", self.recalculate)

        self.target_sparge_temp = target_sparge_temp = Gtk.SpinButton(digits=2, numeric=True)
        target_sparge_temp.set_adjustment(Gtk.Adjustment(165, 0, 180, 0.5, 1, 0))
        target_sparge_temp.connect("value-changed", self.recalculate)

        # button in the center
        self.calculate_button = calculate_button = Gtk.Button(label="Calculate")
        calculate_button.connect("clicked", self.recalculate)

        self.calculated_strike_water = calculated_strike_water = Gtk.Label()
        self.calculated_strike_temp = calculated_strike_temp = Gtk.Label()
        self.calculated_sparge_water = calculated_sparge_water = Gtk.Label()
        self.calculated_sparge_temp = calculated_sparge_temp = Gtk.Label()

        grid = Gtk.Grid(row_spacing=10)
        self.add(grid)

        #inputs
        grid.attach(Gtk.Label("Total Grain Bill (lbs)"), 0, 1, 1, 1)
        grid.attach(grain_bill_lb, 1, 1, 1, 1)
        grid.attach(Gtk.Label("Grist Ratio (qt/lb)"), 0, 2, 1, 1)
        grid.attach(grist_ratio, 1, 2, 1, 1)
        grid.attach(Gtk.Label("Initial Grain Temp (F)"), 0, 3, 1, 1)
        grid.attach(initial_grain_temp, 1, 3, 1, 1)
        grid.attach(Gtk.Label("Empty Mash Tun Temp (F)"), 0, 4, 1, 1)
        grid.attach(empty_tun_temp, 1, 4, 1, 1)
        grid.attach(Gtk.Label("Target Mash Temp (F)"), 0, 5, 1, 1)
        grid.attach(target_mash_temp, 1, 5, 1, 1)
        grid.attach(Gtk.Label("Target Sparge Temp (F)"), 0, 6, 1, 1)
        grid.attach(target_sparge_temp, 1, 6, 1, 1)
        grid.attach(Gtk.Label("Gallons Into Boil"), 0, 7, 1, 1)
        grid.attach(gal_into_boil, 1, 7, 1, 1)

        grid.attach(calculate_button, 0, 8, 2, 1)

        # calculated fields
        grid.attach(Gtk.Label("Strike Water Required (gal)"), 0, 9, 1, 1)
        grid.attach(calculated_strike_water, 1, 9, 1, 1)
        grid.attach(Gtk.Label("Strike Water Temperature (F)"), 0, 10, 1, 1)
        grid.attach(calculated_strike_temp, 1, 10, 1, 1)
        grid.attach(Gtk.Label("Sparge Water Required (gal)"), 0, 11, 1, 1)
        grid.attach(calculated_sparge_water, 1, 11, 1, 1)
        grid.attach(Gtk.Label("Sparge Water Temperature (F)"), 0, 12, 1, 1)
        grid.attach(calculated_sparge_temp, 1, 12, 1, 1)


    def recalculate(self, widget=None):
        grist_ratio = self.grist_ratio.get_value()
        dry_grain_weight = self.grain_bill_lb.get_value()
        initial_grain_temp = self.initial_grain_temp.get_value()
        empty_tun_temp = self.empty_tun_temp.get_value()
        target_mash_temp = self.target_mash_temp.get_value()
        gal_into_boil = self.gal_into_boil.get_value()
        target_sparge_temp = self.target_sparge_temp.get_value()

        # do the math
        strike_water_required = ( dry_grain_weight * grist_ratio ) / 4 # div by 4 to convert qt. to gal
        grain_absorption_gals = calculate_water_absorbed(dry_grain_weight)
        sparge_water_required = (gal_into_boil - strike_water_required) + grain_absorption_gals

        strike_water_temp = calculate_strike_temp(
            target_mash_temp, empty_tun_temp, dry_grain_weight, initial_grain_temp, strike_water_required
        )

        # assume we hit the target mash temp, so now that's used in the calculations
        sparge_water_temp = calculate_sparge_temp(
            target_sparge_temp, target_mash_temp, dry_grain_weight, sparge_water_required
        )

        self.calculated_strike_water.set_text(
            str(round_num(strike_water_required))
        )

        self.calculated_strike_temp.set_text(
            str(round_num(strike_water_temp))
        )
        self.calculated_sparge_water.set_text(
            str(round_num(sparge_water_required))
        )
        self.calculated_sparge_temp.set_text(
            str(round_num(sparge_water_temp))
        )


win = BatchSpageCalculatorWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
