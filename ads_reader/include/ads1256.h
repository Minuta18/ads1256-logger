#ifndef ADS1256_LOGGER_ADS1256_H
#define ADS1256_LOGGER_ADS1256_H

#include <stdint.h>

extern const uint8_t ADS1256_CMD_WAKEUP; /* Completes SYNC and exits standby mode */
extern const uint8_t ADS1256_CMD_RDATA; /* Read data */
extern const uint8_t ADS1256_CMD_RDATAC; /* Read data continuously */
extern const uint8_t ADS1256_CMD_SDATAC; /* Stop read data continuously */
extern const uint8_t ADS1256_CMD_RREG; /* Read from REG */
extern const uint8_t ADS1256_CMD_WREG; /* Write to REG */
extern const uint8_t ADS1256_CMD_SELFCAL; /* Offset and gain self-calibration */
extern const uint8_t ADS1256_CMD_SELFOCAL; /* Offset self-calibration */
extern const uint8_t ADS1256_CMD_SELFGCAL; /* Gain self-calibration */
extern const uint8_t ADS1256_CMD_SYSOCAL; /* System offset calibration */
extern const uint8_t ADS1256_CMD_SYSGCAL; /* System gain calibration */
extern const uint8_t ADS1256_CMD_SYNC; /* Synchronize the A/D conversion  */
extern const uint8_t ADS1256_CMD_STANDBY; /* Begin standby mode */
extern const uint8_t ADS1256_CMD_RESET; /* Reset to power-up values */

extern const uint8_t ADS1256_REG_STATUS;
extern const uint8_t ADS1256_REG_MUX;
extern const uint8_t ADS1256_REG_ADCON;
extern const uint8_t ADS1256_REG_DRATE;
extern const uint8_t ADS1256_REG_IO;
extern const uint8_t ADS1256_REG_OFC0;
extern const uint8_t ADS1256_REG_OFC1;
extern const uint8_t ADS1256_REG_OFC2;
extern const uint8_t ADS1256_REG_FSC0;
extern const uint8_t ADS1256_REG_FSC1;
extern const uint8_t ADS1256_REG_FSC2;

extern const uint8_t ADS1256_PARAM_DRATE_2_5;
extern const uint8_t ADS1256_PARAM_DRATE_5;
extern const uint8_t ADS1256_PARAM_DRATE_10;
extern const uint8_t ADS1256_PARAM_DRATE_15;
extern const uint8_t ADS1256_PARAM_DRATE_25;
extern const uint8_t ADS1256_PARAM_DRATE_30;
extern const uint8_t ADS1256_PARAM_DRATE_50;
extern const uint8_t ADS1256_PARAM_DRATE_60;
extern const uint8_t ADS1256_PARAM_DRATE_100;
extern const uint8_t ADS1256_PARAM_DRATE_500;
extern const uint8_t ADS1256_PARAM_DRATE_1000;
extern const uint8_t ADS1256_PARAM_DRATE_2000;
extern const uint8_t ADS1256_PARAM_DRATE_3750;
extern const uint8_t ADS1256_PARAM_DRATE_7500;
extern const uint8_t ADS1256_PARAM_DRATE_15000;
extern const uint8_t ADS1256_PARAM_DRATE_30000;

extern const uint8_t ADS1256_PARAM_GAIN_1;
extern const uint8_t ADS1256_PARAM_GAIN_2; 
extern const uint8_t ADS1256_PARAM_GAIN_4;
extern const uint8_t ADS1256_PARAM_GAIN_8;
extern const uint8_t ADS1256_PARAM_GAIN_16;
extern const uint8_t ADS1256_PARAM_GAIN_32;
extern const uint8_t ADS1256_PARAM_GAIN_64;

#include "spidev.h"

typedef struct {
        spidev_device_t *spidev;
        uint8_t drate;
        uint8_t gain;

        uint8_t drdy_gpio;
        uint8_t pdwn_gpio;

        char* gpio_name;
} ads1256_config_t;

typedef struct ads1256_device ads1256_device_t;

ads1256_device_t *ads1256_open(const ads1256_config_t *config);
void ads1256_close(ads1256_device_t *device);
int ads1256_reset_chip(ads1256_device_t *device);

int ads1256_gpio_open(ads1256_device_t *device);
void ads1256_gpio_close(ads1256_device_t *device);

int ads1256_wait_drdy(ads1256_device_t *device);
int ads1256_read_channel(ads1256_device_t *device, uint8_t channel, int32_t *out);

#endif // ADS1256_LOGGER_ADS1256_H
