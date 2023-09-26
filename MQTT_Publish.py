import paho.mqtt.client as mqtt
import Crypto.Cipher.AES as AES
import time
import os
#os.system('cls')
meter_id = input("Meter ID? \r\n>>")
key = input("Data Key? (press Enter to use fixkey)\r\n>>")
server_ip = input("Server IP? ([1]IIL(219) [2]IIL(129) [3]ESI)\r\n>>")
fixkey = "000000" + meter_id
topic = meter_id + "S2C"
if key == "" : key = fixkey.encode('utf-8')
else: key = key.encode('utf-8')
if server_ip == "3": 
    server_ip = "52.156.56.170"
    print(server_ip)
else: 
    if server_ip == "2": 
        server_ip = "34.84.143.129"
        print(server_ip)
    else:
        server_ip = "34.96.156.219"
        print(server_ip)

# 鍵値
#key = "000000J200000406".encode('utf-8')
hexkey = bytes.fromhex(key.hex())
iv = "420#abA%,ZfE79@M".encode('utf-8')
hexiv = bytes.fromhex(iv.hex())

# 連線設定
# 初始化地端程式
client = mqtt.Client("P1")

# 設定登入帳號密碼
#client.username_pw_set("try","xxxx")
os.system('cls')
# 設定連線資訊(IP, Port, 連線時間)
client.connect(server_ip, 1883, 600)
while True:
    #command = "c14a200000406f010000000000000000"
    command = input("Hex Command?\r\n>>")
    payload = bytes.fromhex(command)
    decipher =  AES.new(key=hexkey, mode=AES.MODE_CBC, iv=hexiv)
    enc = decipher.encrypt(payload)
    print("Message...:" + enc.hex())
    #要發布的主題和內容
    client.publish(topic, enc)
    time.sleep(1)