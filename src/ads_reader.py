import pipyadc 

class ADSReader:
    def __init__(self, gain: int = 1, drate: int = 2000):
        self.ads = pipyadc.ADS1256()
        self.ads.config_adc(gain, drate)

        self.channels = [i for i in range(8)]

    def read_channels(self) -> list[int]:
        raw_data = self.ads.read_sequence(self.channels)
        return raw_data
    
    def read_channels_in_volts(self) -> list[float]:
        raw_data = self.read_channels()
        return [val * (2.5 / 0x7FFFFF) for val in raw_data]
    