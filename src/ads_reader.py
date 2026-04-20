import pipyadc 
import types

import config

class ADSReader:
    '''Class to manage the ADS1256 reader using pipyadc.'''

    def __init__(self, config_: config.Config):
        self.config = config_
        self.adapter_config = config.LibConfigAdapter(self.config.ads)
        self._ch_seq = self.adapter_config.ch_sequence
        self.ads = None

        # pipyadc expects a module-like object for configuration, so we create 
        # one dynamically from the adapter config. 
        self.lib_config = types.ModuleType('ads_config_runtime')
        for key, value in self.adapter_config.__dict__.items():
            setattr(self.lib_config, key, value)

    def __enter__(self):
        self.ads = pipyadc.ADS1256(self.lib_config)
        self.ads.cal_self()

        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ads is not None:
            self.ads.stop_close_all()

    def read_channels(self) -> list[int]:
        '''Reads the active channels as raw 24-bit values.'''
        assert self.ads is not None, "ADS reader is not initialized."

        raw_data = self.ads.read_continue(self.lib_config.ch_sequence)
        return raw_data
    
    def read_channels_volts(self) -> list[float]:
        '''Reads the active channels as voltage values.'''
        assert self.ads is not None, "ADS reader is not initialized."
        
        raw_data = self.read_channels()
        return [val * self.ads.v_per_digit for val in raw_data]
    