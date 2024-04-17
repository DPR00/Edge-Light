/*
Authors: Miguel Chávez and Diego Palma
Date: 17/04/2024

Techniques and Hardware:
- Using FSK and FFT: each frequency is translated to an instruction
- Using TCS34725 Colour Sensor
- Using TCA9548A 1-to-8 I2C Multiplexer
- Tested on an Arduino Due and the educational robot Maqueen plus v2.

This code performs the following:
(1) Communication with the microbit board through serial port to receive instructions*
(2) change the frequency of the LC based on the received instruction
(3) change the CS to read the indtruction properly
(4) decode the bit from data of the CS. Bits: {2, 4, 5, 8}
(5) It sends the decoded bit to the microbit to change the behaviour of the robot

*Instructions based on the decoded bit:
2: stop robot
4: go backwards
5: rotate
8: go forward
*/

#include "variables.h"

/*
Function to select the color sensor to read data
Source: https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout/arduino-wiring-and-test
*/
void tcaselect(uint8_t i) {
  if (i > 7) return;

  Wire1.beginTransmission(TCAADDR);
  Wire1.write(1 << i);
  Wire1.endTransmission();
}

/*
Interruption function:
 - Read the color sensor data
 - Change decode_fft when is time to decode the frequency
 - Setting blinking frequency of the Liquid crystal 
*/
void txrx_loop() {
  // Every 25 ms

  // Select color sensor to read
  tcaselect(cs_i);
  lux_buffer[i_write] = tcs[cs_i].read16(cs_channel);

  //Calculate mean
  sum_mean += lux_buffer[i_write];

  i_write++;
  // decode signal?
  if (i_write == adc_buffer_size) {
    decode_fft = true;
  }
  i_write = i_write % adc_buffer_size;

  //i_timer counts from 0 to period-1
  i_timer += 1;
  i_timer = i_timer % period;

  // Change frequency of the LC
  if (i_timer % symbol_tx == 0) {
    out1 = out1 ^ 1;
    digitalWrite(lcd1, out1);
  }
}

/*
Funtion to decode the frequency (bit) that the other robot is sending 
*/
uint8_t decode_bit_fft() {
  uint8_t bit = 0;  // Initialize bit
  double m = 0;     // temp real componente
  uint8_t i;        // index to iterate over buffer

  // Eliminate DC component
  for (i = 0; i < adc_buffer_size; i++) {
    vReal[i] = lux_buffer[i];
    vReal[i] -= fft_dc;
    vImag[i] = 0;
  }

  FFT.Compute(FFT_REVERSE);
  FFT.ComplexToMagnitude();

  //All frequencies
  for (i = 0; i <= adc_buffer_size >> 2; i++) {
    if (vReal[i] > m) {
      m = vReal[i];
      bit = i;
    }
  }

  // Send decoded bit to microbit
  Serial.write(bit + 48);
  Serial.write('\n');
  return bit;
}

/*
Function to calibrate the CS
*/
uint8_t calibrate_cs(uint8_t cs_i) {
  tcaselect(cs_i);
  bool sat = true;  //TODO: auto gain-control when saturation/too low gain
  uint8_t i_gain = 0;

  // Sensor exists?
  if (tcs[cs_i].begin(TCS34725_ADDRESS, &Wire1)) {
    ncs_founded++;
  } else {
    while (1)  // break code
      ;
    //return 0;
  }
  tcs[cs_i].setInterrupt(true);  // turn off LED

  /*Avoid USB serial. Use 24ms it and auto-tune gain based on saturation */
  //Take 5 samples and check if channel is saturated.
  while (sat) {
    for (uint8_t i = 0; i < 5; i++) {
      lux_buffer[0] = tcs[cs_i].read16(cs_channel);  // Read channel
      delay(24);                                     // 24 ms integration time
    }
    if (lux_buffer[0] < sat_val) {  //if not saturated, end loop
      sat = false;
    } else {  //decrease gain until minimum.
      i_gain++;
      tcs[cs_i].setGain(cs_g[i_gain]);
      if (i_gain == 3) {
        sat = false;
      }
    }
  }

  selected_igain = i_gain;  // store selected gain

  /*Just for checking: DATA_RATE is the sampling period which needs to be lower than the
    integration time of the colour sensor (when used as a light sensor for demodulation).
    The formula '(256 - _tcs34725IntegrationTime) * 12 / 5 + 1' comes from the colour sensor
    library https://github.com/adafruit/Adafruit_TCS34725/blob/master/Adafruit_TCS34725.cpp
    and gives the integration time in milliseconds */
  if (((256 - cs_it) * 12 / 5 + 1) * 1000 <= DATA_RATE) {
    // Serial.println("IT!");
    ;
  } else {
    while (1)  // break code
      ;
    //return 0;
  }

  return 1;
}

// --------------
// SETUP FUNCTION
// --------------
void setup() {
  Serial.begin(115200);

  for (uint8_t i = 0; i < NUMBER_OF_CS; i++) {
    tcs[i] = Adafruit_TCS34725(cs_it, cs_g[0]);
  }

  //Setting outputs
  out1 = LOW;
  pinMode(13, OUTPUT);
  pinMode(lcd1, OUTPUT);
  digitalWrite(lcd1, out1);

  Wire1.begin();

  for (cs_i = 0; cs_i < NUMBER_OF_CS; cs_i++) {
    if (calibrate_cs(cs_i)) {
    } else {
      Serial.print("Calibration color sensor ");
      Serial.print(cs_i);
      Serial.print(" error.");
    }
  }

  if (MASTER) {
    cs_state = 0;
  } else {
    cs_state = 2;
  }

  cs_i = cs_positions[cs_state];

  Timer3.attachInterrupt(txrx_loop).setPeriod(DATA_RATE).start();
}


// -------------
// LOOP FUNCTION
// -------------
void loop() {

  Serial.flush();  // Clear buffer

  // Read microbit from serial
  if (Serial.available() > 0) {
    stage = Serial.readString();
    uint8_t instr = stage[0] - 48;  // Read instruction. 0: bit 2, 1: bit 4, 2: bit 5 and 3: bit 8.
    if (instr < 4) {
      symbol_tx = bits[instr];  // change freq of LC
      if (instr == 2) {
        period = 15;  // Change period on bit 5
        if (MASTER) change = 1;
      } else {
        period = 16;
        // Change CS for master robot
        if (MASTER) {
          if (change) {
            cs_state = (cs_state + 1) % 4;
            cs_i = cs_positions[cs_state];
            calibrate_cs(cs_i);
            change = 0;
          }
        }
      }
    }
    // Change CS for slave robot
    if (MASTER == 0) {
      if (instr == 9) {
        cs_state = (cs_state + 1) % 4;
        cs_i = cs_positions[cs_state];
      }
    }
  }

  // Decode bit
  if (decode_fft) {
    decode_fft = false;
    fft_dc = sum_mean >> fft_shift;
    sum_mean = 0;
    decode_bit_fft();
  }
}
