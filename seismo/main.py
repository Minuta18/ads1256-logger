import time
import logging
from pipyadc import ADS1256
from pipyadc.utils import TextScreen
from pipyadc.ADS1256_definitions import *
import pipyadc_config

logging.basicConfig(level=logging.DEBUG)

print("\x1B[2J\x1B[H")
print(__doc__)
print("\nPress CTRL-C to exit.\n")

screen = TextScreen()

def text_format_8_ch(digits, volts):
    digits_str = ", ".join([f"{i: 8d}" for i in digits])
    volts_str = ", ".join([f"{i: 8.3f}" for i in volts])
    text = ("    AIN0,     AIN1,     AIN2,     AIN3, "
            "    AIN4,     AIN5,     AIN6,     AIN7\n"
            f"{digits_str}\n\n"
            "Values converted to volts:\n"
            f"{volts_str}\n"
            )
    return text

POTI = POS_AIN0 | NEG_AINCOM
LDR = POS_AIN1 | NEG_AINCOM
CH2 = POS_AIN2 | NEG_AINCOM
CH3 = POS_AIN3 | NEG_AINCOM
CH4 = POS_AIN4 | NEG_AINCOM
CH5 = POS_AIN5 | NEG_AINCOM
CH6 = POS_AIN6 | NEG_AINCOM
CH7 = POS_AIN7 | NEG_AINCOM

CH_SEQUENCE = POTI

def loop_forever_measurements(ads):
    while True:
        raw_channels = ads.read_sequence(CH_SEQUENCE)
        voltages = [i * ads.v_per_digit for i in raw_channels]
        screen.put(text_format_8_ch(raw_channels, voltages))
        screen.refresh()

try:
    with ADS1256(pipyadc_config) as ads:
        ads.drate = DRATE_2000
        ads.cal_self()
        loop_forever_measurements(ads)

except KeyboardInterrupt:
    print("\nUser Exit.\n")
