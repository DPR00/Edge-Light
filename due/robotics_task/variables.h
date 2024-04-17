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

// LSC
volatile bool out1;            // State of the LSC (high or low)
volatile uint8_t i_timer = 0;  // Counter for timer

// Signal and FFT
const uint8_t adc_buffer_size = 32;                               // FIFO buffer size
volatile uint8_t period = 16;                                     // Period of the signal {15, 16}
volatile uint8_t symbol_tx = 8;                                   // Symbol represents the timer divisor for frequency change.
const uint8_t fft_size = 32;                                      // size of fft
const uint8_t fft_shift = 5;                                      // Shift of FFT for DC component
const uint8_t f_sampling = 40;                                    // sampling freq: 1/DATA_RATE
const uint8_t bits[] = { 8, 4, 3, 2 };                            // Bits to decode for FFT
double vReal[fft_size];                                           // Real component of FFT
double vImag[fft_size];                                           // Imag component of FFT
uint16_t fft_dc = 0;                                              // DC component
volatile bool decode_fft = false;                                 // Time to decode?
arduinoFFT FFT = arduinoFFT(vReal, vImag, fft_size, f_sampling);  // FFT Object

// Color sensor (CS)
const uint16_t sat_val = 10240;                                                                         // Value for saturation of the CS
const int lcd1 = 24;                                                                                    // GPIO for LSC
uint16_t lux_buffer[adc_buffer_size];                                                                   // Buffer to store color sensor readings
uint32_t sum_mean = 0;                                                                                  // Mean of the LX of the buffer
uint8_t i_write = 0;                                                                                    // index for writing in the lux buffer
uint8_t cs_channel = TCS34725_RDATAL;                                                                   // Channel based on the color of the LSC. TO DO: Matrix calibration to better find the color of the LSC.
uint8_t cs_it = TCS34725_INTEGRATIONTIME_24MS;                                                          // integration time
uint8_t selected_igain = 0;                                                                             // Gain selected after calibration
uint8_t ncs_founded = 0;                                                                                // CSs founded
uint8_t change = 0;                                                                                     // rotation occured? Then change the state of the color sensor
tcs34725Gain_t cs_g[4] = { TCS34725_GAIN_60X, TCS34725_GAIN_16X, TCS34725_GAIN_4X, TCS34725_GAIN_1X };  // Gains of the CS
Adafruit_TCS34725 tcs[NUMBER_OF_CS] = {};                                                               // Array of the CSs. Created in setup

// CS multiplexing
uint8_t cs_i = 0;                                     // CS index
uint8_t cs_positions[NUMBER_OF_CS] = { 1, 2, 0, 3 };  // CS positions in the robot. 0: front cs, 1: back cs, 2: left cs, 3: right cs.
uint8_t cs_state = 0;                                 // CS that is currently using to decode signal

// Loop
String stage;  // Stage received from Microbit
