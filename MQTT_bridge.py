import paho.mqtt.client as mqtt
import Crypto.Cipher.AES as AES
from datetime import datetime
import time
import os

os.system('cls')
meter_id = input("Meter ID? \r\n>>")
meter_id.replace(" ", "")
meter_type = input("Meter Type? (0:PV / 1:Sub Meter)\r\n>>")
if (meter_type != "1"): meter_type = "0"
key = input("Data Key? (press Enter to use fixkey)\r\n>>")
key.replace(" ", "")
server_ip = input("Server IP? ([1]IIL(219) [2]IIL(129) [3]ESI)\r\n>>")
fixkey = "000000" + meter_id
topic = meter_id + "C2S"
if key == "" : key = fixkey.encode('utf-8')
else: key = key.encode('utf-8')
if server_ip == "3": 
    server_ip = "52.156.56.170"
else: 
    if server_ip == "2": 
        server_ip = "34.84.143.129"
    else:
        server_ip = "34.96.156.219"
#Relay Server Settings
relay_server_ip = input("Relay Server IP? ([1]IIL(219) [2]IIL(129) [3]ESI)\r\n>>")
if relay_server_ip == "3": 
    relay_server_ip = "52.156.56.170"
else: 
    if relay_server_ip == "2": 
        relay_server_ip = "34.84.143.129"
    else:
        relay_server_ip = "34.96.156.219"

# 鍵値
#key = "000000J200000406".encode('utf-8')
hexkey = bytes.fromhex(key.hex())
iv = "420#abA%,ZfE79@M".encode('utf-8')
hexiv = bytes.fromhex(iv.hex())
_ver = ""

meter=[]
if (meter_type == '0'): 
    meter = ["ca", "cc", "", "c2", "c4", "c8", "d4", "d6"]
if (meter_type == '1'): 
    meter = ["2a", "2c", "", "22", "24", "28", "34", "36"]


# 當地端程式連線伺服器得到回應時，要做的動作
def on_connect(client, userdata, flags, rc):
    print("C2S Connected with result code "+str(rc))
    # 將訂閱主題寫在on_connet中
    # 如果我們失去連線或重新連線時 
    # 地端程式將會重新訂閱
    client.subscribe(topic)

# 當接收到從伺服器發送的訊息時要進行的動作
def on_message(client, userdata, msg):
    # Relay msg to relay sever
    # 連線設定
    # 初始化地端程式
    client1 = mqtt.Client(meter_id[4:10]+"w")
    #client1 = mqtt.Client()
    # 設定登入帳號密碼
    #client.username_pw_set("try","xxxx")
    # 設定連線資訊(IP, Port, 連線時間)
    client1.connect(relay_server_ip, 1883, 600)
    client1.publish(topic, msg.payload, qos=2, retain=True)
    ################################################################
    # 轉換編碼utf-8才看得懂中文
    #print(msg.topic+" "+ msg.payload.decode('utf-8'))
    if (msg.payload.hex() != "50"):
        #print(msg.topic+" "+ msg.payload.hex())
        hexmsg = bytes.fromhex(msg.payload.hex())
        decipher =  AES.new(key=hexkey, mode=AES.MODE_CBC, iv=hexiv)
        dec = decipher.decrypt(hexmsg)
        #print('Message...:', dec.hex())
    else: 
        print('Keep Alive')
        return
    if ((dec[0:1].hex() == meter[0]) & (dec[8:9].hex() == "07")) : 
        if (dec[9:12].decode('utf-8') == "CRC"):
            global _ver
            if ((_ver == "V2.19GT7") & (dec[13:23].decode('utf-8') == "0x000064CF")):
                print(_ver + " with CRC " + dec[13:23].decode('utf-8') + " CRC Check OK!")
            else:
                if ((_ver == "V2.20") & (dec[13:23].decode('utf-8') == "0x000025A3")):
                    print(_ver + " with CRC " + dec[13:23].decode('utf-8') + " CRC Check OK!")
                else:
                    if ((_ver == "V2.20G") & (dec[13:23].decode('utf-8') == "0x0000F9A4")):
                        print(_ver + " with CRC " + dec[13:23].decode('utf-8') + " CRC Check OK!")
                    else:
                        if ((_ver == "V1.20") & (dec[13:23].decode('utf-8') == "0x0000A714")):
                            print(_ver + " with CRC " + dec[13:23].decode('utf-8') + " CRC Check OK!")
                        else:
                            print("CRC Check Fail! " + dec[9:].decode('utf-8'))
        else: 
            if (dec[9:17].decode('utf-8') == "SKSENDTO"):
                dis_len = int(dec[69:73].decode('utf-8'),16)
                print(dec[9:74].decode('utf-8')+ " " +dec[74:74+dis_len].hex())
                #SKSENDTO 1 FE80:0000:0000:0000:021D:1291:0000:3F1D 0E1A 1 0 000E
            else:
                print(dec[9:].decode('utf-8'))
    else:
        if (dec[0:1].hex() == meter[1]) :
            if (dec[8:9].hex() == "01") : print('RS485 no response')
            else: print('RS485 Data: ' + dec.hex())
        else:
            if ((dec[0:1].hex() == meter[0]) & (dec[8:9].hex() == "08")) : 
                if ((dec[41:53].decode('utf-8')).strip(" ") == ""): 
                    print("Route B Disabled")
                else:
                    print("RBID: " + dec[9:41].decode('utf-8') + "\n" + "RBPWD: " + dec[41:53].decode('utf-8'))
            else: 
                if (dec[0:1].hex() == meter[3]) : #instant
                    print(datetime.fromtimestamp(int(dec[8:12].hex(),16))) 
                    if(meter_type == '0'):
                        print("RB Import: ", float(int(dec[12:16].hex(),16)/100))
                        print("RB Export: ", float(int(dec[16:20].hex(),16)/100))
                        print("PV Import: ", float(int(dec[20:24].hex(),16)/100))
                    if(meter_type == '1'):
                        print("Import: ", float(int(dec[12:16].hex(),16)/100))
                        print("Export: ", float(int(dec[16:20].hex(),16)/100))
                        print("Pulse Count: ", int(dec[20:24].hex(),16))
                        print("RB Import: ", float(int(dec[24:28].hex(),16)/100))
                        print("RB Export: ", float(int(dec[28:32].hex(),16)/100))
                else:
                    if (dec[0:1].hex() == meter[0]) & ((dec[8:9].hex() == "00")|(dec[8:9].hex() == "01")|(dec[8:9].hex() == "02")) :
                        print('Key Exchange')
                    else:
                        if (dec[0:1].hex() == meter[4]) : #30mins
                            print(datetime.fromtimestamp(int(dec[8:12].hex(),16)))
                            if(meter_type == '0'):
                                print("RB Import: ", float(int(dec[12:16].hex(),16)/100))
                                print("RB Export: ", float(int(dec[16:20].hex(),16)/100))
                                print("PV Import: ", float(int(dec[20:24].hex(),16)/100))
                            if(meter_type == '1'):
                                print("Import: ", float(int(dec[12:16].hex(),16)/100))
                                print("Export: ", float(int(dec[16:20].hex(),16)/100))
                                print("Pulse Count: ", int(dec[20:24].hex(),16))
                                print("RB Import: ", float(int(dec[24:28].hex(),16)/100))
                                print("RB Export: ", float(int(dec[28:32].hex(),16)/100))
                        else:
                            if ((dec[0:1].hex() == meter[0]) & (dec[8:9].hex() == "05")): 
                                print(dec[9:].decode('utf-8'))
                                info = (dec[9:].decode('utf-8')).split('|')
                                _ver = info[3]
                            else:
                                if (dec[0:1].hex() == meter[6]) :
                                    print("Mulit packet data:")
                                    if(meter_type == '0'):
                                        print("Time                    RB Import      RB Emport     PV Import")
                                        for counter in range(10,int((len(dec)-10)/20)*20+10,20):
                                            if (dec[counter:counter+1].hex() != '00'):
                                                print(datetime.fromtimestamp(int(dec[counter:counter+4].hex(),16)), "   ",
                                                    float(int(dec[counter+4:counter+8].hex(),16)/100), "     ",
                                                    float(int(dec[counter+8:counter+12].hex(),16)/100), "    ",
                                                    float(int(dec[counter+12:counter+16].hex(),16)/100))
                                    if(meter_type == '1'):
                                        if (dec[9:10].hex() == "06"):
                                            print("Time                    Import       Export      Pluse       RB Import   RB Emport")
                                            for counter in range(10,int((len(dec)-10)/24)*24+10,24):
                                                if (dec[counter:counter+1].hex() != '00'):        
                                                    print(datetime.fromtimestamp(int(dec[counter:counter+4].hex(),16)), "   ",
                                                        float(int(dec[counter+4:counter+8].hex(),16)/100), "     ",
                                                        float(int(dec[counter+8:counter+12].hex(),16)/100), "    ",
                                                        int(dec[counter+12:counter+16].hex(),16), "    ",
                                                        float(int(dec[counter+16:counter+20].hex(),16)/100), "    ",
                                                        float(int(dec[counter+20:counter+24].hex(),16)/100), "    ",)                       
                                        if (dec[9:10].hex() == "04"):
                                            print("Time                    Import       Emport      Pluse")
                                            for counter in range(10,int((len(dec)-10)/16)*16+10,16):
                                                if (dec[counter:counter+1].hex() != '00'): 
                                                    print(datetime.fromtimestamp(int(dec[counter:counter+4].hex(),16)), "   ",
                                                        float(int(dec[counter+4:counter+8].hex(),16)/100), "     ",
                                                        float(int(dec[counter+8:counter+12].hex(),16)/100), "    ",
                                                        int(dec[counter+12:counter+16].hex(),16), "    ")
                                        if (dec[9:10].hex() == "03"):
                                            print("Time                    Import       Emport")
                                            for counter in range(10,int((len(dec)-10)/12)*12+10,12):
                                                if (dec[counter:counter+1].hex() != '00'):
                                                    print(datetime.fromtimestamp(int(dec[counter:counter+4].hex(),16)), "   ",
                                                        float(int(dec[counter+4:counter+8].hex(),16)/100), "     ",
                                                        float(int(dec[counter+8:counter+12].hex(),16)/100))     
                                else:
                                    if (dec[0:1].hex() == meter[7]) :
                                        print("Eventlog data:")
                                        print("Time                    Import   Export  Record     Event Code")
                                        for counter in range(10,int((len(dec)-10)/16)*16+10,16):
                                            if (dec[counter:counter+1].hex() != '00'):
                                                print(datetime.fromtimestamp(int(dec[counter:counter+4].hex(),16)), "   ",
                                                    float(int(dec[counter+4:counter+8].hex(),16)/100), "   ", #Import
                                                    float(int(dec[counter+8:counter+12].hex(),16)/100), "   ", #Export
                                                    int(dec[counter+12:counter+14].hex(),16), "     ", #Record Num
                                                    dec[counter+14:counter+16].decode('utf-8')) #Event Code
                                    else:
                                        if (dec[0:1].hex() == meter[5]) :
                                            print(datetime.fromtimestamp(int(dec[8:12].hex(),16))) 
                                            print("Current1: ", float(int(dec[12:16].hex(),16)/1000))
                                            print("Voltage1: ", float(int(dec[16:20].hex(),16)/10))
                                            print("Frequency1: ", float(int(dec[20:24].hex(),16)/100))
                                            print("Active PW1: ", float(int(dec[24:28].hex(),16)/10000))
                                            print("Reactive PW1: ", float(int(dec[28:32].hex(),16)/10000))
                                            print("Current2: ", float(int(dec[32:36].hex(),16)/1000))
                                            print("Voltage2: ", float(int(dec[36:40].hex(),16)/10))
                                            print("Frequency2: ", float(int(dec[40:44].hex(),16)/100))
                                            print("Active PW2: ", float(int(dec[44:48].hex(),16)/10000))
                                            print("Reactive PW2: ", float(int(dec[48:52].hex(),16)/10000))                                    
                                        else:
                                            if (dec[0:1].hex() == meter[0]) & ((dec[8:9].hex() == "03")):
                                                print('OTA Package ', int(dec[17:19].hex(),16))
                                            else:
                                                if (dec[0:1].hex() == meter[0]) & ((dec[8:9].hex() == "04")):
                                                    if(dec[9:10].hex() == "00"):
                                                        print('OTA Success')
                                                    else:
                                                        if (dec[9:10].hex() == "01"):
                                                            print('OTA Fail '+ dec[10:11].hex())
                                                            print(dec[11:].decode('utf-8'))
                                                else:
                                                    if (dec[0:1].hex() == "7b"):
                                                        print(dec.decode('utf-8'))
                                                    else:
                                                        print('Message...:', dec.hex())

# 連線設定
# 初始化地端程式
client = mqtt.Client(meter_id[4:10]+"x")

# 設定連線的動作
client.on_connect = on_connect

# 設定接收訊息的動作
client.on_message = on_message

# 設定登入帳號密碼
# client.username_pw_set("try","xxxx")

# 設定連線資訊(IP, Port, 連線時間)
client.connect(server_ip, 1883, 600)

# 開始連線，執行設定的動作和處理重新連線問題
# 也可以手動使用其他loop函式來進行連接
#client.loop_forever()


#########################################################################################
# 當地端程式連線伺服器得到回應時，要做的動作
topic1 = meter_id + "S2C"
def on_connect1(client2, userdata1, flags1, rc):
    print("S2C Connected with result code "+str(rc))
    client2.subscribe(topic1)

# 當接收到從伺服器發送的訊息時要進行的動作
def on_message1(client2, userdata1, msg1):
    # Relay msg to relay sever
    client3 = mqtt.Client(meter_id[4:10]+"y")
    client3.connect(server_ip, 1883, 600)
    client3.publish(topic1, msg1.payload)

client2 = mqtt.Client(meter_id[4:10]+"z")
client2.on_connect = on_connect1
client2.on_message = on_message1
client2.connect(relay_server_ip, 1883, 600)
#client2.loop_forever()

client.loop_start()
client2.loop_start()

while True:
    time.sleep(1)   # 1秒待つ