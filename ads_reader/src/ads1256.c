#include "ads1256.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define ADS1256_TIME_RELOAD 2000

struct ads1256_device {
        spidev_device_t *spidev;
        ads1256_config_t config;
};

static void ads156_delay_us(uint32_t us) {
        usleep(us);
}

ads1256_device_t *ads1256_open(const ads1256_config_t *config)
{
        if (!config) {
                perror("[ADS1256] config is NULL.");
                return NULL;
        }

        ads1256_device_t *device = malloc(sizeof(ads1256_device_t));
        if (!device) {
                perror("[ADS1256] Failed to allocate memory for the ads1256 device.");
                return NULL;
        }

        device->config = *config;
        device->spidev = config->spidev;

        if (ads1256_reset_chip(device) < 0) {
                perror("[ADS1256] Failed to reset chip.");
                goto error_free_device;
        }

        printf("[ADS1256] Initialized successfully.\n");
        return device;
error_free_device:
        free(device);
        return NULL;
}

void ads1256_close(ads1256_device_t *device)
{
        if (!device) { return; }

        printf("[ADS1256] Closing the ads1256 device.\n");

        free(device);
}

int ads1256_reset_chip(ads1256_device_t *device)
{
        if (!device) { return -1; }

        uint8_t cmd = ADS1256_CMD_RESET;
        if (spidev_transfer(device->spidev, &cmd, NULL, 1) < 0) {
                return -1;
        }

        ads156_delay_us(ADS1256_TIME_RELOAD);
        return 0;
}

int ads1256_read_channel(ads1256_device_t *device, uint8_t channel, int32_t *out)
{
        *out = 0;
        return 0; // TODO
}
