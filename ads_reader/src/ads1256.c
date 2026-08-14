#include "ads1256.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

extern const uint8_t ADS1256_CMD_WAKEUP        = 0x00;
extern const uint8_t ADS1256_CMD_RDATA         = 0x01;
extern const uint8_t ADS1256_CMD_RDATAC        = 0x03;
extern const uint8_t ADS1256_CMD_SDATAC        = 0x0F;
extern const uint8_t ADS1256_CMD_RREG          = 0x10;
extern const uint8_t ADS1256_CMD_WREG          = 0x50;
extern const uint8_t ADS1256_CMD_SELFCAL       = 0xF0;
extern const uint8_t ADS1256_CMD_SELFOCAL      = 0xF1;
extern const uint8_t ADS1256_CMD_SELFGCAL      = 0xF2;
extern const uint8_t ADS1256_CMD_SYSOCAL       = 0xF3;
extern const uint8_t ADS1256_CMD_SYSGCAL       = 0xF4;
extern const uint8_t ADS1256_CMD_SYNC          = 0xFC;
extern const uint8_t ADS1256_CMD_STANDBY       = 0xFD;
extern const uint8_t ADS1256_CMD_RESET         = 0xFE;

extern const uint8_t ADS1256_REG_STATUS        = 0x00;
extern const uint8_t ADS1256_REG_MUX           = 0x01;
extern const uint8_t ADS1256_REG_ADCON         = 0x02;
extern const uint8_t ADS1256_REG_DRATE         = 0x03;
extern const uint8_t ADS1256_REG_IO            = 0x04;
extern const uint8_t ADS1256_REG_OFC0          = 0x05;
extern const uint8_t ADS1256_REG_OFC1          = 0x06;
extern const uint8_t ADS1256_REG_OFC2          = 0x07;
extern const uint8_t ADS1256_REG_FSC0          = 0x08;
extern const uint8_t ADS1256_REG_FSC1          = 0x09;
extern const uint8_t ADS1256_REG_FSC2          = 0x0A;

extern const uint8_t ADS1256_PARAM_DRATE_2_5   = 0x03;
extern const uint8_t ADS1256_PARAM_DRATE_5     = 0x13;
extern const uint8_t ADS1256_PARAM_DRATE_10    = 0x23;
extern const uint8_t ADS1256_PARAM_DRATE_15    = 0x33;
extern const uint8_t ADS1256_PARAM_DRATE_25    = 0x43;
extern const uint8_t ADS1256_PARAM_DRATE_30    = 0x53;
extern const uint8_t ADS1256_PARAM_DRATE_50    = 0x63;
extern const uint8_t ADS1256_PARAM_DRATE_60    = 0x72;
extern const uint8_t ADS1256_PARAM_DRATE_100   = 0x82;
extern const uint8_t ADS1256_PARAM_DRATE_500   = 0x92;
extern const uint8_t ADS1256_PARAM_DRATE_1000  = 0xA1;
extern const uint8_t ADS1256_PARAM_DRATE_2000  = 0xB0;
extern const uint8_t ADS1256_PARAM_DRATE_3750  = 0xC0;
extern const uint8_t ADS1256_PARAM_DRATE_7500  = 0xD0;
extern const uint8_t ADS1256_PARAM_DRATE_15000 = 0xE0;
extern const uint8_t ADS1256_PARAM_DRATE_30000 = 0xF0;

extern const uint8_t ADS1256_PARAM_GAIN_1      = 0x00;
extern const uint8_t ADS1256_PARAM_GAIN_2      = 0x01;
extern const uint8_t ADS1256_PARAM_GAIN_4      = 0x02;
extern const uint8_t ADS1256_PARAM_GAIN_8      = 0x03;
extern const uint8_t ADS1256_PARAM_GAIN_16     = 0x04;
extern const uint8_t ADS1256_PARAM_GAIN_32     = 0x05;
extern const uint8_t ADS1256_PARAM_GAIN_64     = 0x06;

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
