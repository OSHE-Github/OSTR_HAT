# PCB design for the Open Source Thunniform Robot Project

### Check us out and find more documentation at oshe.io!

### This is the repository for the versitile Raspberry Pi HAT that was developed for the OSTR project in the Open Source Hardware Enterprise at Michigan Tech. This PCB has the following capabilities:
* Can drive two bidirectional 12 V DC motors or four unidirectional 12 V DC motors
* Can control up to two 5 V servos and read from the feedback potentiometer if it's broken out of the servo. These headers can also be used as 5 V ADC inputs
* Has three 3.3 V ADC headers with 3.3 V and GND available. Can be used to read from a potentiometer.
* Two 3.3 V PWM headers with GND and 5 V
* Two GPIO headers with GND and 3.3 V
* Two 3.3 V I2C headers, one is designed/located to be used with the MPU6050 IMU
* Screw terminal 1-wire port designed for a 1-wire based temperature sensor
* Wide input voltage range of 7 V - 30 V using a DFR1015 buck converter
* Capable of monitoring the input voltage. Useful for running off of a battery
* Capable of measuring the output current of both motor drivers (uses two DRV8874 motor drivers)
* Two audio amplifiers designed to be used with custom built piezo electric disk based transducers