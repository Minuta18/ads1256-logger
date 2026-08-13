#include "spidev.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define SPI_PATH_SIZE 32
#define NO_FILE -1

struct spidev_device {
        int fd;
};

spidev_device_t* spidev_open(const spidev_config_t* config) {
        if (!config) {
                perror("[SPI] Received NULL config.");
                return NULL;
        }

        spidev_device_t *device = malloc(sizeof(spidev_device_t));
        if (!device) {
                perror("[SPI] Failed to allocate memory for SPI device.");
                goto free_device;
        }
        device->fd = NO_FILE;

        return NULL; // TODO

free_device:
        if (device) {
                if (device->fd != NO_FILE) {
                        close(device->fd);
                }
                free(device);
        }

        return NULL;
}
