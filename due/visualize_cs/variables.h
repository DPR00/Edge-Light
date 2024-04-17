#include <CRC8.h>
#include <DueTimer.h>
#include <Wire.h>
#include <Adafruit_TCS34725.h>
#include <arduinoFFT.h>

// Definitions
#define DATA_RATE 25000  // Data rate for timer
#define TCAADDR 0x70     // Mux address
#define NUMBER_OF_CS 4   // Number of color sensors of the robot must be 4.
#define MASTER 0         // is it a mater or slave robot? 0: slave, 1: master

// Signal
const uint8_t adc_buffer_size = 32;
uint16_t lux_buffer_c0[adc_buffer_size];  // Lux buffer for front cs
uint16_t lux_buffer_c1[adc_buffer_size];  // Lux buffer for back cs
uint16_t lux_buffer_c2[adc_buffer_size];  // Lux buffer for left cs
uint16_t lux_buffer_c3[adc_buffer_size];  // Lux buffer for right cs

// Color sensor
const uint16_t sat_val = 10240;                                                                         // Value for saturation of the CS
uint8_t i_write = 0;                                                                                    // index for writing in the lux buffer
uint8_t cs_i = 0;                                                                                       // colour sensor index
uint8_t selected_igain = 0;                                                                             // Gain selected after calibration
uint8_t ncs_founded = 0;                                                                                // CSs founded
uint8_t cs_channel = TCS34725_RDATAL;                                                                   // Channel based on the color of the LSC. TO DO: Matrix calibration to better find the color of the LSC.
uint8_t cs_it = TCS34725_INTEGRATIONTIME_24MS;                                                          // integration time
tcs34725Gain_t cs_g[4] = { TCS34725_GAIN_60X, TCS34725_GAIN_16X, TCS34725_GAIN_4X, TCS34725_GAIN_1X };  // Gains of the CS
Adafruit_TCS34725 tcs[NUMBER_OF_CS] = {};                                                               // Array of the CSs. Created in setup
