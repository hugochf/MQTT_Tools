import paho.mqtt.client as mqtt
import Crypto.Cipher.AES as AES
from datetime import datetime
import time
import os
import ssl

os.system('clear')
meter_id = input("Meter ID? \r\n>>")
meter_id.replace(" ", "")
meter_type = "0"
key = input("Data Key? (press Enter to use fixkey)\r\n>>")
key.replace(" ", "")
fixkey = "000000" + meter_id
topic = meter_id + "C2S"
s2c_topic = meter_id + "S2C"
if key == "":
    key = fixkey.encode('utf-8')
    mkey = fixkey.encode('utf-8')
else:
    key = key.encode('utf-8')
    mkey = input("Master Key?\r\n>>")
    mkey = mkey.encode('utf-8')
server_ip = ""
server_choice = input(
    "Server IP? ([1]IIL(219) [2]IIL(129) [3]ESI [4]Old [5]AWS)\r\n>>")
if server_choice == "3":
    server_ip = "52.156.56.170"
else:
    if server_choice == "2":
        server_ip = "34.84.143.129"
    else:
        if server_choice == "4":
            server_ip = "34.92.152.78"
        else:
            if server_choice == "5":
                server_ip = "a2ki8rxnhuwcg3-ats.iot.ap-east-1.amazonaws.com"
                cacert = './certs/AWS/cacert.pem'
                clientCert = './certs/AWS/clientcert.pem'
                clientKey = './certs/AWS/clientkey.pem'
            else:
                server_ip = "34.96.156.219"

path = str.encode(meter_id + "log.txt")

# 鍵値
# key = "000000J200000406".encode('utf-8')
hexkey = bytes.fromhex(key.hex())
hexmkey = bytes.fromhex(mkey.hex())
iv = "420#abA%,ZfE79@M".encode('utf-8')
hexiv = bytes.fromhex(iv.hex())
_ver = ""

# 當地端程式連線伺服器得到回應時，要做的動作


def on_connect(client, userdata, flags, rc):
    print("C2S Connected with result code "+str(rc))
    client.subscribe(topic)


def on_connect1(client1, userdata1, flags1, rc):
    print("S2C Connected with result code "+str(rc))
    client1.subscribe(s2c_topic)


def on_message1(client1, userdata1, msg1):
    global hexkey, hexmkey
    defaultkey = "69aF7&3KY0_kk89@"
    defaultkey = defaultkey.encode('utf-8')
    hexdefaultkey = bytes.fromhex(defaultkey.hex())
    hexmsg = bytes.fromhex(msg1.payload.hex())
    decipher = AES.new(key=hexdefaultkey, mode=AES.MODE_CBC, iv=hexiv)
    dec1 = decipher.decrypt(hexmsg)
    if ((dec1[0:2].hex() == "c04a") | (dec1[0:2].hex() == "204a") | (dec1[0:2].hex() == "6a4a")) & ((dec1[7:8].hex() == "01")):
        key = bytes.fromhex(dec1[25:41].hex()).decode("ASCII")
        key = key.encode('utf-8')
        hexkey = bytes.fromhex(key.hex())
        print("Data Key: " + bytes.fromhex(key.hex()).decode("ASCII"))
        mkey = bytes.fromhex(dec1[9:25].hex()).decode("ASCII")
        mkey = mkey.encode('utf-8')
        hexmkey = bytes.fromhex(mkey.hex())
        print("Master Key: " + bytes.fromhex(mkey.hex()).decode("ASCII"))
        # Print to file
        now = datetime.now()
        current_time = now.strftime("%Y/%m/%d %H:%M:%S")
        with open(path, 'a', encoding='utf-8') as f:
            f.write(current_time + " S2C: " + dec1.hex() + "\r\n")
            f.close()
    else:
        hexmsg = bytes.fromhex(msg1.payload.hex())
        decipher = AES.new(key=hexmkey, mode=AES.MODE_CBC, iv=hexiv)
        dec1 = decipher.decrypt(hexmsg)
        if ((dec1[0:2].hex() == "c04a") | (dec1[0:2].hex() == "204a") | (dec1[0:2].hex() == "6a4a")) & ((dec1[7:8].hex() == "00")):
            key = bytes.fromhex(dec1[8:24].hex()).decode("ASCII")
            key = key.encode('utf-8')
            print("Data Key: " + bytes.fromhex(key.hex()).decode("ASCII"))
            hexkey = bytes.fromhex(key.hex())
            print("S2C: " + dec1.hex())
            # Print to file
            now = datetime.now()
            current_time = now.strftime("%Y/%m/%d %H:%M:%S")
            with open(path, 'a', encoding='utf-8') as f:
                f.write(current_time + " S2C: " + dec1.hex() + "\r\n")
                f.close()
        else:
            hexmsg = bytes.fromhex(msg1.payload.hex())
            decipher = AES.new(key=hexkey, mode=AES.MODE_CBC, iv=hexiv)
            dec1 = decipher.decrypt(hexmsg)
            # Print to file
            now = datetime.now()
            current_time = now.strftime("%Y/%m/%d %H:%M:%S")
            with open(path, 'a', encoding='utf-8') as f:
                f.write(current_time + " S2C: " + dec1.hex() + "\r\n")
                f.close()
            if (dec1[0:1].hex() == "7b"):
                print(dec1.hex())
                print('S2C: ', bytes.fromhex(dec1.hex()).decode("ASCII"))
            else:
                print('S2C: ', dec1.hex())

# 當接收到從伺服器發送的訊息時要進行的動作


def on_message(client, userdata, msg):
    global hexkey
    # 轉換編碼utf-8才看得懂中文
    # print(msg.topic+" "+ msg.payload.decode('utf-8'))
    if (msg.payload.hex() != "50"):
        # print(msg.topic+" "+ msg.payload.hex())
        hexmsg = bytes.fromhex(msg.payload.hex())
        decipher = AES.new(key=hexkey, mode=AES.MODE_CBC, iv=hexiv)
        dec = decipher.decrypt(hexmsg)
        # Print to file
        now = datetime.now()
        current_time = now.strftime("%Y/%m/%d %H:%M:%S")
        with open(path, 'a', encoding='utf-8') as f:
            f.write(current_time + " C2S: " + dec.hex() + "\r\n")
            f.close()
        print('\nReceived time: ' + current_time)
        # print('Message...:', dec.hex())
    else:
        now = datetime.now()
        current_time = now.strftime("%Y/%m/%d %H:%M:%S")
        with open(path, 'a', encoding='utf-8') as f:
            f.write(current_time + " C2S: " + msg.payload.hex() + "\r\n")
            f.close()
        print('\nReceived time: ' + current_time)
        print('Keep Alive')
        return
    if (dec[2:3].hex() != "4a") & (dec[0:1].hex() != "7b"):
        print('C2S: ', dec.hex())
        return
    if (dec[0:1].hex()[0] == '6') | (dec[0:1].hex()[0] == '7'):
        meter_type = '2'
        meter = ["6a", "6c", "", "62", "64", "68", "74", "76"]
        meter1 = ["6b", "6d", "", "63", "65", "69", "75", "77"]
    else:
        if (dec[0:1].hex()[0] == '2') | (dec[0:1].hex()[0] == '3'):
            meter_type = '1'
            meter = ["2a", "2c", "", "22", "24", "28", "34", "36"]
            meter1 = ["2b", "2d", "", "23", "25", "29", "35", "37"]
        else:
            meter_type = '0'
            meter = ["ca", "cc", "", "c2", "c4", "c8", "d4", "d6"]
            meter1 = ["cb", "cd", "", "c3", "c5", "c9", "d5", "d7"]
    if (((dec[0:1].hex() == meter[0]) | (dec[0:1].hex() == meter1[0])) & (dec[8:9].hex() == "07")):
        if (dec[9:12].decode('utf-8') == "CRC"):
            global _ver
            if ((_ver == "V2.19GT7") & (dec[13:23].decode('utf-8') == "0x000064CF")):
                print(_ver + " with CRC " +
                      dec[13:23].decode('utf-8') + " CRC Check OK!")
            else:
                if ((_ver == "V2.20") & (dec[13:23].decode('utf-8') == "0x000025A3")):
                    print(_ver + " with CRC " +
                          dec[13:23].decode('utf-8') + " CRC Check OK!")
                else:
                    if ((_ver == "V2.20G") & (dec[13:23].decode('utf-8') == "0x0000F9A4")):
                        print(_ver + " with CRC " +
                              dec[13:23].decode('utf-8') + " CRC Check OK!")
                    else:
                        if ((_ver == "V1.20") & (dec[13:23].decode('utf-8') == "0x0000A714")):
                            print(_ver + " with CRC " +
                                  dec[13:23].decode('utf-8') + " CRC Check OK!")
                        else:
                            print("CRC Check Fail! " + dec[9:].decode('utf-8'))
        else:
            if (dec[9:17].decode('utf-8') == "SKSENDTO"):
                dis_len = int(dec[69:73].decode('utf-8'), 16)
                print(dec[9:73].decode('utf-8') +
                      " " + dec[74:74+dis_len].hex())
                # SKSENDTO 1 FE80:0000:0000:0000:021D:1291:0000:3F1D 0E1A 1 0 000E
            else:
                print(dec[9:].decode('utf-8', 'ignore'))
    else:
        if (dec[0:1].hex() == meter[1]) | (dec[0:1].hex() == meter1[1]):
            if (dec[8:9].hex() == "01"):
                print('RS485 no response')
            else:
                print('RS485 Data: ' + dec.hex())
        else:
            if (((dec[0:1].hex() == meter[0]) | (dec[0:1].hex() == meter1[0])) & (dec[8:9].hex() == "08")):
                if ((dec[41:53].decode('utf-8')).strip(" ") == ""):
                    print("Route B Disabled")
                else:
                    print("RBID: " + dec[9:41].decode('utf-8') +
                          "\n" + "RBPWD: " + dec[41:53].decode('utf-8'))
            else:
                if (dec[0:1].hex() == meter[3]) | (dec[0:1].hex() == meter1[3]):  # instant
                    print(datetime.fromtimestamp(int(dec[8:12].hex(), 16)))
                    if (meter_type == '0'):
                        print("RB Import: ", float(
                            int(dec[12:16].hex(), 16)/100))
                        print("RB Export: ", float(
                            int(dec[16:20].hex(), 16)/100))
                        print("PV Import: ", float(
                            int(dec[20:24].hex(), 16)/100))
                    if (meter_type == '1'):
                        print("Import: ", float(int(dec[12:16].hex(), 16)/100))
                        print("Export: ", float(int(dec[16:20].hex(), 16)/100))
                        print("Pulse Count: ", int(dec[20:24].hex(), 16))
                        print("RB Import: ", float(
                            int(dec[24:28].hex(), 16)/100))
                        print("RB Export: ", float(
                            int(dec[28:32].hex(), 16)/100))
                else:
                    if ((dec[0:1].hex() == meter[0]) | (dec[0:1].hex() == meter1[0])) & ((dec[8:9].hex() == "00") | (dec[8:9].hex() == "01") | (dec[8:9].hex() == "02")):
                        print('Key Exchange')
                    else:
                        if (dec[0:1].hex() == meter[4]) | (dec[0:1].hex() == meter1[4]):  # 30mins
                            print(datetime.fromtimestamp(
                                int(dec[8:12].hex(), 16)))
                            if (meter_type == '0'):
                                print("RB Import: ", float(
                                    int(dec[12:16].hex(), 16)/100))
                                print("RB Export: ", float(
                                    int(dec[16:20].hex(), 16)/100))
                                print("PV Import: ", float(
                                    int(dec[20:24].hex(), 16)/100))
                            if (meter_type == '1'):
                                print("Import: ", float(
                                    int(dec[12:16].hex(), 16)/100))
                                print("Export: ", float(
                                    int(dec[16:20].hex(), 16)/100))
                                print("Pulse Count: ", int(
                                    dec[20:24].hex(), 16))
                                print("RB Import: ", float(
                                    int(dec[24:28].hex(), 16)/100))
                                print("RB Export: ", float(
                                    int(dec[28:32].hex(), 16)/100))
                        else:
                            if (((dec[0:1].hex() == meter[0]) | (dec[0:1].hex() == meter1[0])) & (dec[8:9].hex() == "05")):
                                print(dec[9:].decode('utf-8'))
                                info = (dec[9:].decode('utf-8')).split('|')
                                _ver = info[3]
                            else:
                                if (dec[0:1].hex() == meter[6]) | (dec[0:1].hex() == meter1[6]):
                                    print("Mulit packet data:")
                                    if (meter_type == '0'):
                                        print(
                                            "Time                    RB Import      RB Emport     PV Import")
                                        for counter in range(10, int((len(dec)-10)/20)*20+10, 20):
                                            if (dec[counter:counter+1].hex() != '00'):
                                                print(datetime.fromtimestamp(int(dec[counter:counter+4].hex(), 16)), "   ",
                                                      float(
                                                          int(dec[counter+4:counter+8].hex(), 16)/100), "     ",
                                                      float(
                                                          int(dec[counter+8:counter+12].hex(), 16)/100), "    ",
                                                      float(int(dec[counter+12:counter+16].hex(), 16)/100))
                                    if (meter_type == '1'):
                                        if (dec[9:10].hex() == "06"):
                                            print(
                                                "Time                    Import       Export      Pluse       RB Import   RB Emport")
                                            for counter in range(10, int((len(dec)-10)/24)*24+10, 24):
                                                if (dec[counter:counter+1].hex() != '00'):
                                                    print(datetime.fromtimestamp(int(dec[counter:counter+4].hex(), 16)), "   ",
                                                          float(
                                                              int(dec[counter+4:counter+8].hex(), 16)/100), "     ",
                                                          float(
                                                              int(dec[counter+8:counter+12].hex(), 16)/100), "    ",
                                                          int(dec[counter+12:counter +
                                                              16].hex(), 16), "    ",
                                                          float(
                                                              int(dec[counter+16:counter+20].hex(), 16)/100), "    ",
                                                          float(int(dec[counter+20:counter+24].hex(), 16)/100), "    ",)
                                        if (dec[9:10].hex() == "04"):
                                            print(
                                                "Time                    Import       Emport      Pluse")
                                            for counter in range(10, int((len(dec)-10)/16)*16+10, 16):
                                                if (dec[counter:counter+1].hex() != '00'):
                                                    print(datetime.fromtimestamp(int(dec[counter:counter+4].hex(), 16)), "   ",
                                                          float(
                                                              int(dec[counter+4:counter+8].hex(), 16)/100), "     ",
                                                          float(
                                                              int(dec[counter+8:counter+12].hex(), 16)/100), "    ",
                                                          int(dec[counter+12:counter+16].hex(), 16), "    ")
                                        if (dec[9:10].hex() == "03"):
                                            print(
                                                "Time                    Import       Emport")
                                            for counter in range(10, int((len(dec)-10)/12)*12+10, 12):
                                                if (dec[counter:counter+1].hex() != '00'):
                                                    print(datetime.fromtimestamp(int(dec[counter:counter+4].hex(), 16)), "   ",
                                                          float(
                                                              int(dec[counter+4:counter+8].hex(), 16)/100), "     ",
                                                          float(int(dec[counter+8:counter+12].hex(), 16)/100))
                                else:
                                    if (dec[0:1].hex() == meter[7]) | (dec[0:1].hex() == meter1[7]):
                                        print("Eventlog data:")
                                        print(
                                            "Time                    Import   Export  Record     Event Code")
                                        for counter in range(10, int((len(dec)-10)/16)*16+10, 16):
                                            if (dec[counter:counter+1].hex() != '00'):
                                                print(datetime.fromtimestamp(int(dec[counter:counter+4].hex(), 16)), "   ",
                                                      # Import
                                                      float(
                                                          int(dec[counter+4:counter+8].hex(), 16)/100), "   ",
                                                      # Export
                                                      float(
                                                          int(dec[counter+8:counter+12].hex(), 16)/100), "   ",
                                                      # Record Num
                                                      int(dec[counter+12:counter + \
                                                          14].hex(), 16), "     ",
                                                      dec[counter+14:counter+16].decode('utf-8'))  # Event Code
                                    else:
                                        if (dec[0:1].hex() == meter[5]) | (dec[0:1].hex() == meter1[5]):
                                            print(datetime.fromtimestamp(
                                                int(dec[8:12].hex(), 16)))
                                            print("Current1: ", float(
                                                int(dec[12:16].hex(), 16)/1000))
                                            print("Voltage1: ", float(
                                                int(dec[16:20].hex(), 16)/10))
                                            print("Frequency1: ", float(
                                                int(dec[20:24].hex(), 16)/100))
                                            print("Active PW1: ", float(
                                                int(dec[24:28].hex(), 16)/10000))
                                            print("Reactive PW1: ", float(
                                                int(dec[28:32].hex(), 16)/10000))
                                            print("Current2: ", float(
                                                int(dec[32:36].hex(), 16)/1000))
                                            print("Voltage2: ", float(
                                                int(dec[36:40].hex(), 16)/10))
                                            print("Frequency2: ", float(
                                                int(dec[40:44].hex(), 16)/100))
                                            print("Active PW2: ", float(
                                                int(dec[44:48].hex(), 16)/10000))
                                            print("Reactive PW2: ", float(
                                                int(dec[48:52].hex(), 16)/10000))
                                        else:
                                            if ((dec[0:1].hex() == meter[0]) | (dec[0:1].hex() == meter1[0])) & ((dec[8:9].hex() == "03")):
                                                print('OTA Package ', int(
                                                    dec[17:19].hex(), 16))
                                            else:
                                                if ((dec[0:1].hex() == meter[0]) | (dec[0:1].hex() == meter[0])) & ((dec[8:9].hex() == "04")):
                                                    if (dec[9:10].hex() == "00"):
                                                        print('OTA Success')
                                                    else:
                                                        if (dec[9:10].hex() == "01"):
                                                            print(
                                                                'OTA Fail ' + dec[10:11].hex())
                                                            print(
                                                                dec[11:].decode('utf-8'))
                                                else:
                                                    if (dec[0:1].hex() == "7b"):
                                                        print(
                                                            dec.decode('utf-8'))
                                                    else:
                                                        print(
                                                            'Message...:', dec.hex())


# 連線設定
# 初始化地端程式
client = mqtt.Client(meter_id[4:10]+"z")
client1 = mqtt.Client(meter_id[4:10]+"y")

if server_choice == "5":
    client.tls_set(cacert,
                   certfile=clientCert,
                   keyfile=clientKey,
                   tls_version=ssl.PROTOCOL_TLSv1_2)
    client.tls_insecure_set(True)

    client1.tls_set(cacert,
                    certfile=clientCert,
                    keyfile=clientKey,
                    tls_version=ssl.PROTOCOL_TLSv1_2)
    client1.tls_insecure_set(True)

# 設定連線的動作
client.on_connect = on_connect
client1.on_connect = on_connect1
# 設定接收訊息的動作
client.on_message = on_message
client1.on_message = on_message1
# 設定登入帳號密碼
# client.username_pw_set("try","xxxx")
# 設定連線資訊(IP, Port, 連線時間)
if server_choice == "5":
    client.connect(server_ip, 8883, 600)
    client1.connect(server_ip, 8883, 600)
else:
    client.connect(server_ip, 1883, 600)
    client1.connect(server_ip, 1883, 600)
# 開始連線，執行設定的動作和處理重新連線問題
# 也可以手動使用其他loop函式來進行連接
client.loop_start()
client1.loop_start()

while True:
    time.sleep(1)   # 1秒待つ
