import xmlrpc.client
import time

fl = xmlrpc.client.ServerProxy("http://127.0.0.1:7362/")

print(fl.main.set_afc(False))
print(fl.main.get_afc())
print(fl.modem.set_carrier(1500))
print(fl.modem.get_carrier())


fl.text.clear_tx()
fl.text.clear_rx()

print(fl.modem.get_name())
print(fl.modem.set_by_name("MFSK4"))
print(fl.modem.get_name())

print("init tx start")
fl.text.add_tx("init^r")
fl.main.tx()
print("init tx command send done")
while not(str(fl.main.get_trx_status()) == 'rx'):
    time.sleep(0.1)
print("init tx done")

rx=""

while(1):
    print("1")
    rx = rx + str(fl.rx.get_data())
    print(rx)
    start = rx.find("MSG")
    if(not(start == -1)):
        print(f"cmd start at {start}, rx: {rx}")
        end = rx.find("END")
        if(not(end == -1)):
            rx = rx.replace("MSG","")
            rx = rx.replace("END","")
            print(f"Command recieved: {rx}")
            rx=""        
    elif(not(rx.endswith("MS") or rx.endswith("M"))):
        print("clear")
        rx=""
    else:
        print(f"start detect: {rx}")

    time.sleep(0.5)
        

