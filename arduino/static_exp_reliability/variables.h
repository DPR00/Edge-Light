#include <CRC8.h>
#include <DueTimer.h>
#include <Wire.h>
#include <Adafruit_TCS34725.h>
#include <arduinoFFT.h>

// Definitions
#define DATA_RATE 25000  // Data rate for timer
#define TCAADDR 0x70     // Mux address
#define NUMBER_OF_CS 2   // Number of color sensors of the robot must be 2. (Evaluate front and back)
#define MASTER 0         // is it a mater or slave robot? 0: slave, 1: master2
// LSC
volatile bool out1;            // State of the LSC (high or low)
volatile uint8_t i_timer = 0;  // Counter for timer

// Signal and FFT
const uint8_t adc_buffer_size = 32;                               // FIFO buffer size
volatile uint8_t period = 15;                                     // Period of the signal {15, 16}
volatile uint8_t symbol_tx = 3;                                   // Symbol represents the timer divisor for frequency change. CHANGE
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
uint8_t cs_i = 0;                                                                                       // colour sensor index
uint8_t channels[2] = { TCS34725_RDATAL, TCS34725_GDATAL };                                             // Options for channel (RED and GREEN LSC)
uint8_t cs_channel = channels[MASTER];                                                                  // Channel based on the color of the LSC. TO DO: Matrix calibration to better find the color of the LSC.
uint8_t cs_it = TCS34725_INTEGRATIONTIME_24MS;                                                          // integration time
uint8_t selected_igain = 0;                                                                             // Gain selected after calibration
uint8_t ncs_founded = 0;                                                                                // CSs founded
uint8_t change = 0;                                                                                     // rotation occured? Then change the state of the color sensor
tcs34725Gain_t cs_g[4] = { TCS34725_GAIN_60X, TCS34725_GAIN_16X, TCS34725_GAIN_4X, TCS34725_GAIN_1X };  // Gains of the CS
Adafruit_TCS34725 tcs[2] = { Adafruit_TCS34725(cs_it, cs_g[0]), Adafruit_TCS34725(cs_it, cs_g[0]) };    // Array of the CSs. Created in setup


// Log data
int i_log = 0;          // index to know when start logging lux_buffer
int b_log = 0;          // index to knwo when start logging decoded bit
uint8_t start_log = 0;  // Flag to start logging
const uint8_t log_buffer_size = 255;
uint16_t lux_log[log_buffer_size];  // buffer for logging cs reading
uint8_t bit_log[log_buffer_size];   // buffer for logging decoded bits

// Loop
String stage;  // Stage received from Microbit
double threshold = 3; // bit2: 4, bit4: 3, bit5: 2, bit 8: 3