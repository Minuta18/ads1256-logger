# ADS1256 Logger

![Python](https://img.shields.io/badge/Code-Python-informational?style=flat&logo=python&color=3776AB)
![Linux](https://img.shields.io/badge/System-Linux-informational?style=flat&logo=linux&color=FCC624)

An application for reading data from the ADS1256 and storing the collected data.

## Features

- **Configuration**: Project is designed to be configurable as much as possible. Config is stored in convenient TOML format.
- **Asynchronous file operations**: High-performance asynchronous handling of file I/O to ensure smooth data saving without blocking on one-core devices.
- **Basic GPS integration**: Support for basic GPS functionality to timestamp and geolocate data readings.
- **Experimental web interface**: A web-based interface for monitoring and managing data collection in real-time. The web interface is experimental and may be removed in the future. 
