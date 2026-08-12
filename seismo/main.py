import time
import logging
from pipyadc import ADS1256
from pipyadc.ADS1256_definitions import *
import pipyadc_config

logging.basicConfig(level=logging.WARNING)

print("\x1B[2J\x1B[H")
print("ADS1256 single-channel (AIN0) speed test.")
print("\nPress CTRL-C to exit.\n")

CH_SEQUENCE = (POS_AIN0 | NEG_AINCOM,)

def loop_forever_measurements(ads):
    sample_count = 0
    start_time = time.perf_counter()
    print_interval = 1.0

    while True:
        raw_channels = ads.read_sequence(CH_SEQUENCE)
        
        sample_count += 1
        current_time = time.perf_counter()
        elapsed = current_time - start_time

        if elapsed >= print_interval:
            sps = sample_count / elapsed
            voltage = raw_channels[0] * ads.v_per_digit
            
            print(
                f"Speed: {sps:6.1f} samples/sec | "
                f"AIN0 Raw: {raw_channels[0]:8d} | "
                f"AIN0 Volts: {voltage:7.4f}V"
            )
            
            sample_count = 0
            start_time = current_time

try:
    with ADS1256(pipyadc_config) as ads:
        ads.drate = DRATE_2000
        ads.cal_self()
        loop_forever_measurements(ads)

except KeyboardInterrupt:
    print("\nUser Exit.\n")
