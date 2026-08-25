#include "spidev.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>

#define SPI_PATH_SIZE 32
#define NO_FILE -1

struct spidev_device {
        int fd;
        spidev_config_t config;
};

static void spidev_construct_path(
        const spidev_config_t* config,
        char* buf,
        const size_t len)
{
        snprintf(buf, len, "/dev/spidev%u.%u", config->spi_bus, config->chip_select);
}

spidev_device_t* spidev_open(const spidev_config_t* config)
{
        if (!config) {
                perror("[SPI] Received NULL config.");
                return NULL;
        }

        spidev_device_t *device = malloc(sizeof(spidev_device_t));
        if (!device) {
                perror("[SPI] Failed to allocate memory for SPI device.");
                return NULL;
        }
        device->fd = NO_FILE;
        device->config = *config;

        char spi_path[SPI_PATH_SIZE];
        spidev_construct_path(&(device->config), spi_path, sizeof(spi_path));

        printf("[SPI] Opening SPI device: %s\n", spi_path);
        device->fd = open(spi_path, O_RDWR);
        if (device->fd < 0) {
                perror("[SPI] Failed to open SPI device.");
                goto free_device_and_exit;
        }

        uint8_t mode = device->config.spi_mode;
        if (ioctl(device->fd, SPI_IOC_WR_MODE, &mode) < 0) {
                perror("[SPI] Failed to set SPI mode.");
                goto free_device_and_exit;
        }

        uint8_t bits = device->config.spi_bits;
        if (ioctl(device->fd, SPI_IOC_WR_BITS_PER_WORD, &bits) < 0) {
                perror("[SPI] Failed to set SPI bits per word.");
                goto free_device_and_exit;
        }

        uint32_t speed = device->config.spi_speed_hz;
        if (ioctl(device->fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed) < 0) {
                perror("[SPI] Failed to set SPI speed.");
                goto free_device_and_exit;
        }

        printf("[SPI] Initialized successfully.\n");
        return device;

free_device_and_exit:
        if (device) {
                spidev_close(device);
        }
        return NULL;
}

void spidev_close(spidev_device_t* device)
{
        if (!device) { return; }

        if (device->fd != NO_FILE)
                close(device->fd);

        free(device);
}

int spidev_transfer(
        spidev_device_t* device,
        const uint8_t *transfer_buf,
        uint8_t *receive_buf,
        size_t length)
{
        if (!device || length == 0) { return -1; }

        uint8_t *tx = (uint8_t *)transfer_buf;
        uint8_t *rx = receive_buf;
        int allocated_tx = 0;
        int allocated_rx = 0;

        if (!tx) {
                tx = calloc(length, sizeof(uint8_t));
                if (!tx) return -1;
                allocated_tx = 1;
        }

        if (!rx) {
                rx = malloc(length);
                if (!rx) {
                        if (allocated_tx) free(tx);
                        return -1;
                }
                allocated_rx = 1;
        }

        struct spi_ioc_transfer tr = {
                .tx_buf = (unsigned long)tx,
                .rx_buf = (unsigned long)rx,
                .len = length,
                .speed_hz = device->config.spi_speed_hz,
                .delay_usecs = 0,
                .bits_per_word = device->config.spi_bits,
        };

        if (ioctl(device->fd, SPI_IOC_MESSAGE(1), &tr) < 0) {
                perror("[SPI] Failed to send SPI transfer.");
                if (allocated_tx) free(tx);
                if (allocated_rx) free(rx);
                return -1;
        }

        if (allocated_tx) free(tx);
        if (allocated_rx) free(rx);

        return 0;
}

const spidev_config_t* spidev_get_config(spidev_device_t* device)
{
        return &(device->config);
}