#ifndef ADS1256_LOGGER_ADS1256_H
#define ADS1256_LOGGER_ADS1256_H

#define ADS1256_CMD_WAKEUP        0x00 /* Completes SYNC and exits standby mode */
#define ADS1256_CMD_RDATA         0x01 /* Read data */
#define ADS1256_CMD_RDATAC        0x03 /* Read data continuously */
#define ADS1256_CMD_SDATAC        0x0F /* Stop read data continuously */
#define ADS1256_CMD_RREG          0x10 /* Read from REG */
#define ADS1256_CMD_WREG          0x50 /* Write to REG */
#define ADS1256_CMD_SELFCAL       0xF0 /* Offset and gain self-calibration */
#define ADS1256_CMD_SELFOCAL      0xF1 /* Offset self-calibration */
#define ADS1256_CMD_SELFGCAL      0xF2 /* Gain self-calibration */
#define ADS1256_CMD_SYSOCAL       0xF3 /* System offset calibration */
#define ADS1256_CMD_SYSGCAL       0xF4 /* System gain calibration */
#define ADS1256_CMD_SYNC          0xFC /* Synchronize the A/D conversion  */
#define ADS1256_CMD_STANDBY       0xFD /* Begin standby mode */
#define ADS1256_CMD_RESET         0xFE /* Reset to power-up values */

#define ADS1256_REG_STATUS        0x00
#define ADS1256_REG_MUX           0x01
#define ADS1256_REG_ADCON         0x02
#define ADS1256_REG_DRATE         0x03
#define ADS1256_REG_IO            0x04
#define ADS1256_REG_OFC0          0x05
#define ADS1256_REG_OFC1          0x06
#define ADS1256_REG_OFC2          0x07
#define ADS1256_REG_FSC0          0x08
#define ADS1256_REG_FSC1          0x09
#define ADS1256_REG_FSC2          0x0A

#define ADS1256_PARAM_DRATE_2_5   0x03
#define ADS1256_PARAM_DRATE_5     0x13
#define ADS1256_PARAM_DRATE_10    0x23
#define ADS1256_PARAM_DRATE_15    0x33
#define ADS1256_PARAM_DRATE_25    0x43
#define ADS1256_PARAM_DRATE_30    0x53
#define ADS1256_PARAM_DRATE_50    0x63
#define ADS1256_PARAM_DRATE_60    0x72
#define ADS1256_PARAM_DRATE_100   0x82
#define ADS1256_PARAM_DRATE_500   0x92
#define ADS1256_PARAM_DRATE_1000  0xA1
#define ADS1256_PARAM_DRATE_2000  0xB0
#define ADS1256_PARAM_DRATE_3750  0xC0
#define ADS1256_PARAM_DRATE_7500  0xD0
#define ADS1256_PARAM_DRATE_15000 0xE0
#define ADS1256_PARAM_DRATE_30000 0xF0

#define ADS1256_PARAM_GAIN_1      0x00
#define ADS1256_PARAM_GAIN_2      0x01
#define ADS1256_PARAM_GAIN_4      0x02
#define ADS1256_PARAM_GAIN_8      0x03
#define ADS1256_PARAM_GAIN_16     0x04
#define ADS1256_PARAM_GAIN_32     0x05
#define ADS1256_PARAM_GAIN_64     0x06

#include "spidev.h"

typedef struct {
        spidev_device_t *spidev;
        uint8_t drate;
        uint8_t gain;
} ads1256_config_t;

typedef struct ads1256_device ads1256_device_t;

ads1256_device_t *ads1256_open(const ads1256_config_t *config);
void ads1256_close(ads1256_device_t *device);

int ads1256_reset_chip(ads1256_device_t *device);
int ads1256_read_channel(ads1256_device_t *device, uint8_t channel, int32_t *out);

#endif // ADS1256_LOGGER_ADS1256_H
