from xmlrpc.client import boolean
import paho.mqtt.client as mqtt
import Crypto.Cipher.AES as AES
from datetime import datetime
import time
import os
global meter_id
global meter_type

flag = 0
os.system('clear')
meter_id = input("Meter ID? \r\n>>")
meter_id.replace(" ", "")
fixkey = "000000" + meter_id
defaultkey = "69aF7&3KY0_kk89@"
meter_type = input("Meter Type? (0:PV / 1:Sub Meter / 2:GateWay)\r\n>>")
if (meter_type != "1") and (meter_type != "2") : meter_type = "0"
server_ip = input("Server IP? ([1]IIL(219) [2]IIL(129) [3]ESI)\r\n>>")
ex_type = input("[1]as Meter or [2]as Server?\r\n>>")
if (ex_type != "1"): ex_type = "2"
cmd = input("[1]Full KeyEx [2]Disconnect KeyEx?\r\n>>")
if (cmd == "1")&(ex_type == "1"):
    dkey = fixkey.encode('utf-8')
    mkey = fixkey.encode('utf-8')
    defaultkey = defaultkey.encode('utf-8')
else: 
    dkey = input("Data Key? (press Enter to use fixkey)\r\n>>")
    dkey.replace(" ", "")
    if dkey == "" :
        dkey = fixkey.encode('utf-8')
        mkey = fixkey.encode('utf-8')
        defaultkey = defaultkey.encode('utf-8')
    else:
        mkey = input("Master Key?\r\n>>")
        dkey = dkey.encode('utf-8')
        mkey = mkey.encode('utf-8')
        defaultkey = defaultkey.encode('utf-8')

c2s_topic = meter_id + "C2S"
s2c_topic = meter_id + "S2C"
if server_ip == "3": 
    server_ip = "52.156.56.170"
else: 
    if server_ip == "2": 
        server_ip = "34.84.143.129"
    else:
        server_ip = "34.96.156.219"
hexdefaultkey = bytes.fromhex(defaultkey.hex())
hexdkey = bytes.fromhex(dkey.hex())
hexmkey = bytes.fromhex(mkey.hex())
iv = "420#abA%,ZfE79@M".encode('utf-8')
hexiv = bytes.fromhex(iv.hex())

meter=[]
if (meter_type == '0'): 
    meter = ["ca", "c04a"]
if (meter_type == '1'): 
    meter = ["2a", "204a"]
if (meter_type == '2'): 
    meter = ["6a", "604a"]

###############################################################################
if (ex_type == "2"): #as Server
    def on_connect(client, userdata, flags, rc):
        print("C2S Connected with result code "+str(rc))
        client.subscribe(c2s_topic)
    def on_message(client, userdata, msg):
        global flag
        global cmd
        global meter_id
        global meter_type

        if (cmd == "2"): #Disconnect Key-Ex
            command = ""
            if (flag > 0):
                key=hexdkey
            else:
                key=hexmkey
            if (msg.payload.hex() != "50"):
                hexmsg = bytes.fromhex(msg.payload.hex())
                decipher =  AES.new(key, mode=AES.MODE_CBC, iv=hexiv)
                dec = decipher.decrypt(hexmsg)
            else: 
                print('Keep Alive')
                return           
            if (dec[0:1].hex() == meter[0]) & ((dec[8:9].hex() == "01")) : #6a004a224d0047950100000000000000
                print("C2S: Request change key")
                print(dec.hex())
                if (meter_type != '2'):
                    command = meter[1] + meter_id.strip("J?") + "F00" + dkey.hex()
                if (meter_type == '2'): 
                    meter_id = meter_id.replace("M", "4D")
                    command = meter[1] + meter_id.strip("J?") + "00" + dkey.hex()
                print("C2S: Response data key")
                key=hexmkey
                flag =+ 1
            else:
                if (dec[0:1].hex() == meter[0]) & ((dec[8:9].hex() == "02")) :
                        print("C2S: Request success ACK")
                        print(dec.hex())
                        if (meter_type != '2'):
                            command = meter[1] + meter_id.strip("J?") + "F02"
                        if (meter_type == '2'):
                            meter_id = meter_id.replace("M", "4D")
                            command = meter[1] + meter_id.strip("J?") + "02"
                        print("S2C: Confirm data key")
                        print("Master Key: " + bytes.fromhex(mkey.hex()).decode("ASCII"))
                        print("Data Key: " + bytes.fromhex(dkey.hex()).decode("ASCII"))
                        key=hexdkey
                else:
                    print('Message...:', dec.hex())
            if (command != ""):
                while (len(command)%32 !=0): 
                    command += "0"
                print(command)
                payload = bytes.fromhex(command)
                decipher =  AES.new(key, mode=AES.MODE_CBC, iv=hexiv)
                enc = decipher.encrypt(payload)
                client1 = mqtt.Client(meter_id[4:10]+"r")
                client1.connect(server_ip, 1883, 600)
                client1.publish(s2c_topic, enc)

        if (cmd == "1"): #Full Key-Ex
            command = ""
            key=hexdefaultkey
            if (msg.payload.hex() != "50"):
                hexmsg = bytes.fromhex(msg.payload.hex())
                decipher =  AES.new(key, mode=AES.MODE_CBC, iv=hexiv)
                dec = decipher.decrypt(hexmsg)
            else: 
                print('Keep Alive')
                return
            if (dec[0:1].hex() == meter[0]) & ((dec[8:9].hex() == "00")) :
                print("C2S: Request registration")
                print(dec.hex())    
                if (meter_type != '2'):
                    command = meter[1] + meter_id.strip("J?") + "F0120" + mkey.hex() + dkey.hex()
                if (meter_type == '2'): 
                    meter_id = meter_id.replace("M", "4D")
                    command = meter[1] + meter_id.strip("J?") + "0120" + mkey.hex() + dkey.hex()        
                print("C2S: Registration data")
            else:
                if (dec[0:1].hex() == meter[0]) & ((dec[8:9].hex() == "02")) :
                    print("C2S: success ACK")
                    print(dec.hex())
                    cmd = "2"
                else:
                    print('Message...:', dec.hex())
            if (command != ""):
                while (len(command)%32 !=0): 
                    command += "0"
                print(command)
                payload = bytes.fromhex(command)
                decipher =  AES.new(key, mode=AES.MODE_CBC, iv=hexiv)
                enc = decipher.encrypt(payload)
                client1 = mqtt.Client(meter_id[4:10]+"r")
                client1.connect(server_ip, 1883, 600)
                client1.publish(s2c_topic, enc)
    client = mqtt.Client(meter_id[4:10]+"s")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(server_ip, 1883, 600)
    client.loop_start()
    while True:
        time.sleep(1)   # 1秒待つ

###############################################################################
if (ex_type == "1"): #as Meter
    key_done = False
    def on_connect(client, userdata, flags, rc):
        print("S2C Connected with result code "+str(rc))
        client.subscribe(s2c_topic)

    def on_message(client, userdata, msg):
        global hexdefaultkey, hexmkey, hexdkey
        global mkey, dkey
        global cmd
        global flag
        global meter_id
        global meter_type

        if (cmd == "2"): #Disconnect Key-Ex
            global key_done
            command = ""
            if (flag > 0):
                key=hexdkey
            else:
                key=hexmkey
            if (msg.payload.hex() != "50"):
                hexmsg = bytes.fromhex(msg.payload.hex())
                decipher =  AES.new(key, mode=AES.MODE_CBC, iv=hexiv)
                dec = decipher.decrypt(hexmsg)
            else: 
                print('Keep Alive')
                return
            if (dec[0:2].hex() == meter[1]) & ((dec[7:8].hex() == "00")) :
                print("S2C: Response data key")
                print(dec.hex())
                print("\r")
                dkey = bytes.fromhex(dec[8:24].hex()).decode("ASCII")
                dkey = dkey.encode('utf-8')
                hexdkey = bytes.fromhex(dkey.hex())
                if (meter_type != '2'):
                    command = meter[0] + "004a" + meter_id.strip("J?") + "F02"
                if (meter_type == '2'): 
                    meter_id = meter_id.replace("M", "4D")
                    command = meter[0] + "004a" + meter_id.strip("J?") + "02"               
                print("C2S: Request success ACK - Dis")
                key = hexdkey
                flag =+ 1
            else:
                if (dec[0:2].hex() == meter[1]) & ((dec[7:8].hex() == "02")) :
                    command = ""
                    print("S2C: Confirm new key")
                    print(dec.hex())
                    print("Master Key: " + bytes.fromhex(mkey.hex()).decode("ASCII"))
                    print("Data Key: " + bytes.fromhex(dkey.hex()).decode("ASCII"))
                    print("\r")
                    time.sleep(1)
                    #command = meter[0] + "004a" + meter_id.strip("J?") + "F083030"
                    flag = 0
                    key_done = True
                else:
                    print('Message...:', dec.hex())
        
        if (cmd == "1"): #Full Key-Ex
            key = hexdefaultkey
            command = ""
            if (msg.payload.hex() != "50"):
                hexmsg = bytes.fromhex(msg.payload.hex())
                decipher =  AES.new(key, mode=AES.MODE_CBC, iv=hexiv)
                dec = decipher.decrypt(hexmsg)
            else: 
                print('Keep Alive')
                return
            if (dec[0:2].hex() == meter[1]) & ((dec[7:8].hex() == "01")) :
                print("S2C: Registration data")
                print(dec.hex())
                print("\r")         
                dkey = bytes.fromhex(dec[9:25].hex()).decode("ASCII")
                dkey = dkey.encode('utf-8')
                hexdkey = bytes.fromhex(dkey.hex())
                mkey = bytes.fromhex(dec[25:41].hex()).decode("ASCII")
                mkey = mkey.encode('utf-8')
                hexmkey = bytes.fromhex(mkey.hex())
                if (meter_type != '2'):
                    command = meter[0] + "004a" + meter_id.strip("J?") + "F02"
                if (meter_type == '2'): 
                    meter_id = meter_id.replace("M", "4D")
                    command = meter[0] + "004a" + meter_id.strip("J?") + "02"     
                print("Master Key: " + bytes.fromhex(mkey.hex()).decode("ASCII"))
                print("Data Key: " + bytes.fromhex(dkey.hex()).decode("ASCII"))
                print("\r")
                print("C2S: Request success ACK - Full")
                cmd = "2"
            else:
                print('Message...:', dec.hex())

        if (command != ""):
            while (len(command)%32 !=0):
                command += "0"
            print(command)
            print("\r")
            payload = bytes.fromhex(command)
            decipher =  AES.new(key, mode=AES.MODE_CBC, iv=hexiv)
            enc = decipher.encrypt(payload)
            client1 = mqtt.Client(meter_id[4:10]+"r")
            client1.connect(server_ip, 1883, 600)
            client1.publish(c2s_topic, enc)
        else:
            return

    client = mqtt.Client(meter_id[4:10]+"s")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(server_ip, 1883, 600)
    client.loop_start()

    while (not key_done) :
        if (cmd == "2"):
            key = hexmkey
            #Start Key exchange 
            if (meter_type != '2'):
                command = meter[0] + "004a" + meter_id.strip("J?") + "F01"
            if (meter_type == '2'): 
                meter_id = meter_id.replace("M", "4D")
                command = meter[0] + "004a" + meter_id.strip("J?") + "01"     
            print("C2S: Request change key - Dis")
        if (cmd == "1"):
            key = hexdefaultkey
            #Start MASTER Key exchange
            if (meter_type != '2'):
                command = meter[0] + "004a" + meter_id.strip("J?") + "F00"
            if (meter_type == '2'): 
                meter_id = meter_id.replace("M", "4D")
                command = meter[0] + "004a" + meter_id.strip("J?") + "00"         
            print("C2S: Request change key - Full")
        if (command != ""):
            while (len(command)%32 !=0): 
                command += "0"
        print(command)
        print("\r")
        payload = bytes.fromhex(command)
        decipher =  AES.new(key, mode=AES.MODE_CBC, iv=hexiv)
        enc = decipher.encrypt(payload)
        client1 = mqtt.Client(meter_id[4:10]+"r")
        client1.connect(server_ip, 1883, 600)
        client1.publish(c2s_topic, enc)
        time.sleep(15)   # 1秒待つ
