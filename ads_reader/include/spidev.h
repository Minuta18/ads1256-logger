#ifndef ADS1256_LOGGER_SPIDEV_H
#define ADS1256_LOGGER_SPIDEV_H

#include <stdint.h>
#include <stddef.h>

typedef struct spidev_device spidev_device_t;

typedef struct {
        uint32_t spi_speed;
        uint8_t  spi_mode;
        uint8_t  spi_bus;
        uint8_t  chip_select;
} spidev_config_t;

spidev_device_t* spidev_open(const spidev_config_t* config);
void spidev_close(spidev_device_t* device);
int spidev_transfer(
        spidev_device_t* device,
        const uint8_t *transfer_buf,
        const uint8_t *receive_buf,
        size_t length
);

#endif // ADS1256_LOGGER_SPIDEV_H
