/*
Authors: Miguel Chávez and Diego Palma
Date: 17/04/2024

Hardware:
- Using TCS34725 Colour Sensor
- Using TCA9548A 1-to-8 I2C Multiplexer
- Tested on an Arduino Due and the educational robot Maqueen plus v2.

This code performs the following:
(1) Read data from four color sensors and print them over Serial. Visualize them over Serial plotter
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
 - Read the color sensor data and save data in a buffer
*/
void txrx_loop() {
  // every 25 ms

  // Read and save front cs
  tcaselect(0);
  tcs[0].setGain(cs_g[selected_igain]);
  lux_buffer_c0[i_write] = tcs[0].read16(cs_channel);

  // Read and save back cs
  tcaselect(1);
  tcs[1].setGain(cs_g[selected_igain]);
  lux_buffer_c1[i_write] = tcs[1].read16(cs_channel);

  // Read and save left cs
  tcaselect(2);
  tcs[2].setGain(cs_g[selected_igain]);
  lux_buffer_c2[i_write] = tcs[2].read16(cs_channel);

  // Read and save right cs
  tcaselect(3);
  tcs[3].setGain(cs_g[selected_igain]);
  lux_buffer_c3[i_write] = tcs[3].read16(cs_channel);

  i_write++;
  i_write = i_write % adc_buffer_size;
}


/*
Function to calibrate the CS
*/
uint8_t calibrate_cs(uint8_t cs_i, uint16_t lux_buffer[]) {
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

  Wire1.begin();

  if (calibrate_cs(0, lux_buffer_c0)) {
  } else {
    Serial.print("Calibration color sensor ");
    Serial.print(0);
    Serial.print(" error.");
  }

  if (calibrate_cs(1, lux_buffer_c1)) {
  } else {
    Serial.print("Calibration color sensor ");
    Serial.print(1);
    Serial.print(" error.");
  }

  if (calibrate_cs(2, lux_buffer_c2)) {
  } else {
    Serial.print("Calibration color sensor ");
    Serial.print(2);
    Serial.print(" error.");
  }

  if (calibrate_cs(3, lux_buffer_c3)) {
  } else {
    Serial.print("Calibration color sensor ");
    Serial.print(3);
    Serial.print(" error.");
  }

  cs_i = MASTER;

  Serial.print("Sensors founded: "), Serial.println(ncs_founded);
  Timer3.attachInterrupt(txrx_loop).setPeriod(DATA_RATE).start();
}

// -------------
// LOOP FUNCTION
// -------------
void loop() {

  // Print lux values of each sensor (visualize with Serial Plotter)
  Serial.print(lux_buffer_c0[i_write - 1]);
  Serial.print(", ");
  Serial.print(lux_buffer_c1[i_write - 1]);
  Serial.print(", ");
  Serial.print(lux_buffer_c2[i_write - 1]);
  Serial.print(", ");
  Serial.println(lux_buffer_c3[i_write - 1]);
}
