#include "ads1256.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <gpiod.h>

const uint8_t ADS1256_CMD_WAKEUP        = 0x00;
const uint8_t ADS1256_CMD_RDATA         = 0x01;
const uint8_t ADS1256_CMD_RDATAC        = 0x03;
const uint8_t ADS1256_CMD_SDATAC        = 0x0F;
const uint8_t ADS1256_CMD_RREG          = 0x10;
const uint8_t ADS1256_CMD_WREG          = 0x50;
const uint8_t ADS1256_CMD_SELFCAL       = 0xF0;
const uint8_t ADS1256_CMD_SELFOCAL      = 0xF1;
const uint8_t ADS1256_CMD_SELFGCAL      = 0xF2;
const uint8_t ADS1256_CMD_SYSOCAL       = 0xF3;
const uint8_t ADS1256_CMD_SYSGCAL       = 0xF4;
const uint8_t ADS1256_CMD_SYNC          = 0xFC;
const uint8_t ADS1256_CMD_STANDBY       = 0xFD;
const uint8_t ADS1256_CMD_RESET         = 0xFE;

const uint8_t ADS1256_REG_STATUS        = 0x00;
const uint8_t ADS1256_REG_MUX           = 0x01;
const uint8_t ADS1256_REG_ADCON         = 0x02;
const uint8_t ADS1256_REG_DRATE         = 0x03;
const uint8_t ADS1256_REG_IO            = 0x04;
const uint8_t ADS1256_REG_OFC0          = 0x05;
const uint8_t ADS1256_REG_OFC1          = 0x06;
const uint8_t ADS1256_REG_OFC2          = 0x07;
const uint8_t ADS1256_REG_FSC0          = 0x08;
const uint8_t ADS1256_REG_FSC1          = 0x09;
const uint8_t ADS1256_REG_FSC2          = 0x0A;

const uint8_t ADS1256_PARAM_DRATE_2_5   = 0x03;
const uint8_t ADS1256_PARAM_DRATE_5     = 0x13;
const uint8_t ADS1256_PARAM_DRATE_10    = 0x23;
const uint8_t ADS1256_PARAM_DRATE_15    = 0x33;
const uint8_t ADS1256_PARAM_DRATE_25    = 0x43;
const uint8_t ADS1256_PARAM_DRATE_30    = 0x53;
const uint8_t ADS1256_PARAM_DRATE_50    = 0x63;
const uint8_t ADS1256_PARAM_DRATE_60    = 0x72;
const uint8_t ADS1256_PARAM_DRATE_100   = 0x82;
const uint8_t ADS1256_PARAM_DRATE_500   = 0x92;
const uint8_t ADS1256_PARAM_DRATE_1000  = 0xA1;
const uint8_t ADS1256_PARAM_DRATE_2000  = 0xB0;
const uint8_t ADS1256_PARAM_DRATE_3750  = 0xC0;
const uint8_t ADS1256_PARAM_DRATE_7500  = 0xD0;
const uint8_t ADS1256_PARAM_DRATE_15000 = 0xE0;
const uint8_t ADS1256_PARAM_DRATE_30000 = 0xF0;

const uint8_t ADS1256_PARAM_GAIN_1      = 0x00;
const uint8_t ADS1256_PARAM_GAIN_2      = 0x01;
const uint8_t ADS1256_PARAM_GAIN_4      = 0x02;
const uint8_t ADS1256_PARAM_GAIN_8      = 0x03;
const uint8_t ADS1256_PARAM_GAIN_16     = 0x04;
const uint8_t ADS1256_PARAM_GAIN_32     = 0x05;
const uint8_t ADS1256_PARAM_GAIN_64     = 0x06;

#define ADS1256_TIME_RELOAD_MS 5
#define ADS1256_DRDY_TIMEOUT_MS 500

int32_t parse_24bit(const uint8_t *buf)
{
        int32_t raw_value = ((int32_t)buf[0] << 16) |
                            ((int32_t)buf[1] << 8)  |
                            (int32_t)buf[2];

        if (raw_value & 0x800000) {
                raw_value |= 0xFF000000;
        }

        return raw_value;
}

struct ads1256_device {
        spidev_device_t *spidev;
        ads1256_config_t config;

        struct gpiod_line_request *drdy_line;
};

ads1256_device_t *ads1256_open(const ads1256_config_t *config)
{
        if (!config) {
                perror("[ADS1256] config is NULL.");
                return NULL;
        }

        ads1256_device_t *device = malloc(sizeof(ads1256_device_t));
        if (!device) {
                perror("[ADS1256] Failed to allocate memory.");
                return NULL;
        }

        device->config = *config;
        device->spidev = config->spidev;
        device->drdy_line = NULL;

        if (ads1256_gpio_open(device) < 0) {
                perror("[ADS1256] Failed to setup GPIO.");
                goto error_free_device;
        }

        usleep(50000);

        if (ads1256_reset_chip(device) < 0) {
                perror("[ADS1256] Failed to reset chip.");
                goto error_free_device;
        }

        if (ads1256_diagnostics(device) < 0) {
                fprintf(stderr, "[ADS1256] WARNING: Hardware diagnostics check failed.\n");
        }

        printf("[ADS1256] Initialized successfully.\n");
        return device;

error_free_device:
        ads1256_close(device);
        return NULL;
}

void ads1256_close(ads1256_device_t *device)
{
        if (!device) { return; }

        printf("[ADS1256] Closing the ads1256 device.\n");
        ads1256_gpio_close(device);
        free(device);
}

int ads1256_reset_chip(ads1256_device_t *device)
{
        if (!device) { return -1; }

        uint8_t cmd = ADS1256_CMD_RESET;
        if (spidev_transfer(device->spidev, &cmd, NULL, 1) < 0) {
                return -1;
        }

        usleep(ADS1256_TIME_RELOAD_MS * 1000);

        cmd = ADS1256_CMD_SDATAC;
        if (spidev_transfer(device->spidev, &cmd, NULL, 1) < 0) {
                return -1;
        }

        usleep(ADS1256_TIME_RELOAD_MS * 1000);
        return 0;
}

int ads1256_gpio_open(ads1256_device_t *device)
{
        struct gpiod_chip *chip = gpiod_chip_open(device->config.gpio_name);
        if (!chip) {
                fprintf(stderr, "[GPIO] Failed to open chip at %s\n", device->config.gpio_name);
                return -1;
        }

        struct gpiod_line_settings *settings = gpiod_line_settings_new();
        if (!settings) {
                gpiod_chip_close(chip);
                return -1;
        }
        gpiod_line_settings_set_direction(settings, GPIOD_LINE_DIRECTION_INPUT);

        unsigned int drdy_offset = device->config.drdy_gpio;

        struct gpiod_line_config *line_cfg = gpiod_line_config_new();
        if (!line_cfg) {
                gpiod_line_settings_free(settings);
                gpiod_chip_close(chip);
                return -1;
        }
        gpiod_line_config_add_line_settings(line_cfg, &drdy_offset, 1, settings);

        struct gpiod_request_config *req_cfg = gpiod_request_config_new();
        if (req_cfg) {
                gpiod_request_config_set_consumer(req_cfg, "ads1256_drdy");
        }

        device->drdy_line = gpiod_chip_request_lines(chip, req_cfg, line_cfg);

        if (req_cfg) gpiod_request_config_free(req_cfg);
        gpiod_line_config_free(line_cfg);
        gpiod_line_settings_free(settings);
        gpiod_chip_close(chip);

        if (!device->drdy_line) {
                fprintf(stderr, "[GPIO] Failed to request DRDY line %d\n", device->config.drdy_gpio);
                return -1;
        }

        return 0;
}

void ads1256_gpio_close(ads1256_device_t *device)
{
        if (device && device->drdy_line) {
                gpiod_line_request_release(device->drdy_line);
                device->drdy_line = NULL;
        }
}

int ads1256_wait_drdy(ads1256_device_t *device)
{
        if (!device || !device->drdy_line) return -1;

        unsigned int drdy_offset = device->config.drdy_gpio;

        for (int i = 0; i < ADS1256_DRDY_TIMEOUT_MS; i++) {
                if (gpiod_line_request_get_value(device->drdy_line, drdy_offset) == 0) {
                        return 0;
                }
                usleep(1000);
        }

        fprintf(stderr, "[ADS1256] Timeout waiting for DRDY\n");
        return -1;
}

int ads1256_read_reg(ads1256_device_t *device, uint8_t reg, uint8_t *out_val)
{
        if (!device || !out_val) return -1;

        if (ads1256_wait_drdy(device) < 0) {
                return -1;
        }

        uint8_t tx_buf[2] = { (uint8_t)(ADS1256_CMD_RREG | reg), 0x00 };
        if (spidev_transfer(device->spidev, tx_buf, NULL, 2) < 0) {
                return -1;
        }

        usleep(10);

        uint8_t rx_val = 0;
        if (spidev_transfer(device->spidev, NULL, &rx_val, 1) < 0) {
                return -1;
        }

        *out_val = rx_val;
        return 0;
}

int ads1256_read_channel(ads1256_device_t *device, uint8_t channel, int32_t *out)
{
        if (!device || !out) { return -1; }

        *out = 0;
        if (ads1256_wait_drdy(device) < 0) {
                return -1;
        }

        uint8_t mux_value = (channel << 4) | 0x08;
        uint8_t wreg_packet[3] = {
                ADS1256_CMD_WREG | ADS1256_REG_MUX,
                0x00,
                mux_value
        };

        if (spidev_transfer(device->spidev, wreg_packet, NULL, 3) < 0) {
                perror("[ADS1256] Failed to write MUX register\n");
                return -1;
        }

        uint8_t sync_wakeup[2] = { ADS1256_CMD_SYNC, ADS1256_CMD_WAKEUP };
        if (spidev_transfer(device->spidev, sync_wakeup, NULL, 2) < 0) {
                perror("[ADS1256] Failed to send SYNC, WAKEUP commands\n");
                return -1;
        }

        if (ads1256_wait_drdy(device) < 0) {
                return -1;
        }

        uint8_t rdata_cmd = ADS1256_CMD_RDATA;
        if (spidev_transfer(device->spidev, &rdata_cmd, NULL, 1) < 0) {
                perror("[ADS1256] Failed to send RDATA command\n");
                return -1;
        }

        uint8_t rx_buf[3] = { 0x00, 0x00, 0x00 };
        if (spidev_transfer(device->spidev, NULL, rx_buf, 3) < 0) {
                perror("[ADS1256] Failed to read data\n");
                return -1;
        }

        *out = parse_24bit(rx_buf);
        return 0;
}

int ads1256_diagnostics(ads1256_device_t *device)
{
        if (!device) return -1;

        uint8_t status_val = 0;
        if (ads1256_read_reg(device, ADS1256_REG_STATUS, &status_val) < 0) {
                fprintf(stderr, "[ADS1256] Diagnostics: Failed to read STATUS register via SPI.\n");
                return -1;
        }

        printf("[ADS1256] Diagnostics: STATUS register value = 0x%02X\n", status_val);

        if (status_val == 0x00 || status_val == 0xFF) {
                fprintf(stderr, "[ADS1256] Diagnostics: STATUS register unchanged. Diagnostics failed.\n");
                return -1;
        }

        return 0;
}