from smbus2 import SMBus
import time
## ADC

# ADC I2C Address
ADDRADC = 0x48

# ADC pins
MD0I = 0
MD1I = 1
SADC2 = 2
SADC3 = 3
VBATT = 7

# Command Byte
SEINPUTS = 0x80 # Differential inputs
DEINPUTS = 0x00 # Single-ended inputs
CSSHIFT = 4     # shift to apply to desired pin
PDMODE = 0x04   # power-down mode (Internal Reference OFF and A/D Converter ON)

## PWM

# PWM chip I2C Address
ADDRPWM = 0x1C

# Define various registers
MODE1 = 0x00
MODE2 = 0x01
PWM0 = 0x02
LEDOUT0 = 0x0C  # pins 0-3
LEDOUT1 = 0x0D  # pins 4-7

# Define control bytes
CTRL = 0x00
CTRLAI = 0x80   # Autoincrement flag


## Motor Drivers

# Driver 0 PWM pins
M0P1 = 1
M0P2 = 0

# Driver 1 PWM pins
M1P1 = 3
M1P2 = 2

# Motor driver modes
MDMRC = 0
MDMFC = 1
MDMFB = 2
MDMRB = 3

#defaut delay
DEFDELAY = 0.1

class ADC:
    def __init__(self, addr, i2cbus):
        self.addr = addr        # I2C address of chip
        self.i2cbus = i2cbus
    
    def read(self, pin):
        print("ADC read")
        print(f"Control byte: {SEINPUTS | (pin << CSSHIFT) | PDMODE}")
        self.i2cbus.write_byte(self.addr, SEINPUTS | (pin << CSSHIFT) | PDMODE)  # Initiate a read on pin
        return self.i2cbus.read_byte(self.addr)                                  # Get ADC reading and return it

class PWMExpander:
    def __init__(self, addr, i2cbus):
        self.addr = addr        # I2C address of chip
        self.i2cbus = i2cbus
        #control byte = 1000 0000 0x80
        # MODE1: 1000 0000 0x80
        # MODE2: 0000 0101 0x05
        print(f"MODE: {self.i2cbus.read_i2c_block_data(self.addr, CTRLAI, 18)}")
        #print(f"MODE1: {self.i2cbus.read_i2c_block_data(self.addr, 0, 1)}")
        #print(f"MODE2: {self.i2cbus.read_i2c_block_data(self.addr, 1, 1)}")
        #time.sleep(10)
        self.i2cbus.write_i2c_block_data(self.addr, CTRLAI, [0x00, 0x15])
        time.sleep(DEFDELAY)
        print(f"MODE: {self.i2cbus.read_i2c_block_data(self.addr, CTRLAI, 18)}")
        
    # set PWM duty cycle and set pin mode to PWM
    # pin 0x00 - 0x07
    # duty - 0-255, duty cycle = duty/256
    def setPWM(self, pin, duty):
        print("PWM setPWM")
        self.setPINMODE(pin, 0)                                     # turn pin off
        print(f"Control byte: {PWM0 + pin}, Duty: {duty}")
        self.i2cbus.write_byte_data(self.addr, PWM0 + pin, duty)    # write duty to pin PWM register
        time.sleep(DEFDELAY)
        print(f"MODE: {self.i2cbus.read_i2c_block_data(self.addr, CTRLAI, 18)}")
        self.setPINMODE(pin, 2)                                     # enable PWM on pin
        
    
    # set pin output mode
    # 0 - off; 1 - on; 2 - PWM
    def setPINMODE(self, pin, mode):
        print("PWM setPINMODE")
        pinStates = self.i2cbus.read_i2c_block_data(self.addr, CTRLAI | (LEDOUT0),2)      # get current state
        print(f"Control Byte: {CTRLAI | (LEDOUT0 + int(pin/4))}")
        print(f"Current pinStates: {pinStates}")
        pinStates[int(pin/4)] = pinStates[int(pin/4)] & (0xFF^(0x3 << 2*(pin%4)))   # clear bits associated with given pin
        pinStates[int(pin/4)] = pinStates[int(pin/4)] | (mode << 2*(pin%4))         # set bits associated with given pin to mode
            
        print(f"New pinStates: {pinStates}")
        self.i2cbus.write_i2c_block_data(self.addr, CTRLAI | (LEDOUT0), pinStates)      # set new state
        time.sleep(DEFDELAY)
        print(f"MODE: {self.i2cbus.read_i2c_block_data(self.addr, CTRLAI, 18)}")
        

## Motor Drivers

class motorDriver:
    # pwmexpander - PWMExpander object that controls the IO expander
    # pinEN - PWMExpander pin connected to EN_IN1 pin
    # pinPH = PWMExpander pin connected to PH_IN2 pin
    def __init__(self, pwmexpander, pin1, pin2):
        self.pin = [0,0]
        self.pin[0] = pin1
        self.pin[1] = pin2
        self.pwmexpander = pwmexpander
        
    # mode - left = constant pin state; right = constant pin
    # 0 - 00 - coast; reverse
    # 1 - 01 - coast; forward
    # 2 - 10 - brake; forward
    # 3 - 11 - brake; reverse
    # duty = 0-256, duty cycle = duty/256
    def go(self, mode, duty):
        print("Motor go")
        print(f"Pin: {self.pin[mode%2]}, Mode: {int(mode/2)}")
        self.pwmexpander.setPINMODE(self.pin[mode%2], int(mode/2))     # set value of constant pin
        
        if duty > 255:
            print(f"Pin: {self.pin[1-mode%2]}, Mode: 1")
            self.pwmexpander.setPINMODE(self.pin[1-mode%2], 1)
            
        else:
            print(f"Pin: {self.pin[1-mode%2]}, Duty: {duty}")
            self.pwmexpander.setPWM(self.pin[1-mode%2], duty)
            
    
    # mode - 0 = coast; 1 = brake
    def stop(self, mode):
        print("Motor stop")
        self.pwmexpander.setPINMODE(self.pin[0], mode)
        self.pwmexpander.setPINMODE(self.pin[1], mode)
        
# Test code

i2cbus = SMBus(1)
print("\nADC init")
adc = ADC(ADDRADC, i2cbus)
print("\npwmexpander init")
pwmexpander = PWMExpander(ADDRPWM, i2cbus)
print("\nmotor0 init")
motor0 = motorDriver(pwmexpander, M0P1, M0P2)
print("\nmotor1 init")
motor1 = motorDriver(pwmexpander, M1P1, M1P2)

for i in range(7):
    print(i)
    pwmexpander.setPINMODE(i, 0)
