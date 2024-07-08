import paho.mqtt.client as mqtt
import Crypto.Cipher.AES as AES
import time
import os

os.system('clear')
meter_id = input("Meter ID? \r\n>>")
meter_id.replace(" ", "")
meter_id2 = meter_id
meter_type = input("Meter Type? (0:PV / 1:Sub Meter / 2:Gateway)\r\n>>")
if (meter_type != "1") & (meter_type != "2"):
    meter_type = "0"
key = input("Data Key? (press Enter to use fixkey)\r\n>>")
key.replace(" ", "")
server_ip = input("Server IP? ([1]IIL(219) [2]IIL(129) [3]ESI [4]Old)\r\n>>")
fixkey = "000000" + meter_id
topic = meter_id + "S2C"
if key == "":
    key = fixkey.encode('utf-8')
else:
    key = key.encode('utf-8')
if server_ip == "3":
    server_ip = "52.156.56.170"
    print(server_ip)
else:
    if server_ip == "2":
        server_ip = "34.84.143.129"
        print(server_ip)
    else:
        if server_ip == "4":
            server_ip = "34.92.152.78"
        else:
            server_ip = "34.96.156.219"

# 鍵値
# key = "000000J200000406".encode('utf-8')
hexkey = bytes.fromhex(key.hex())
iv = "420#abA%,ZfE79@M".encode('utf-8')
hexiv = bytes.fromhex(iv.hex())

rbid = ""
rbpwd = ""
command = ""
meter = []
if (meter_type == '0'):
    meter = ["C04A", "C14A", "", "", "", "", "C64A", "C74A", "C84A"]
    meter_id = meter_id + "F"
if (meter_type == '1'):
    meter = ["204A", "214A", "", "", "", "", "264A", "274A", "284A"]
    meter_id = meter_id + "F"
if (meter_type == '2'):
    meter = ["604A", "614A", "", "", "", "", "664A", "674A", "684A"]
    meter_id = meter_id.replace("M", "4D")
    meter_id = meter_id.replace("P", "50")

# 連線設定
# 初始化地端程式
client = mqtt.Client('P1')
# 設定登入帳號密碼
# client.username_pw_set("try","xxxx")
# 設定連線資訊(IP, Port, 連線時間)
# client.connect(server_ip, 1883, 600)
while True:
    os.system('clear')
    print("***********" + meter_id2 + "S2C CMD List**************\r")
    print("0. Get Instant\r")
    print("1. Get Route B info\r")
    print("2. Set Route B ID & PWD\r")
    print("3. Disable Route B\r")
    print("4. Get Connection Diagnostic\r")
    print("5. Reset Pointer\r")
    print("6. Reset Meter\r")
    print("7. Reset Module\r")
    print("8. Start Route B Diagnostic\r")
    print("9. Get Version Info\r")
    print("10. CRC Check\r")
    print("11. Get Power Line Info\r")
    print("12. Get Event Log\r")
    print("13. Get 30-min Log\r")
    print("14. Set Meter Option\r")
    print("15. Set IP address & Port\r")
    print("16. PCS Monitoring\r")
    print("17. Get Slave Meter Info\r")
    print("18. JSON command\r")
    print("19. Disconnect Key-Exchange (Server side)\r")
    print("99. Send Manual Command\r")
    print("***********************************************\r")
    option = input("Which Command?\r\n>>")

    if option == "0":
        command = meter[1] + meter_id.strip("J?") + "01"
    else:
        if option == "1":
            command = meter[7] + meter_id.strip("J?") + "00"
        else:
            if option == "3":
                command = meter[7] + meter_id.strip("J?") + "023030"
            else:
                if option == "4":
                    command = meter[1] + meter_id.strip("J?") + "07"
                else:
                    if option == "5":
                        command = meter[6] + meter_id.strip("J?") + "00"
                    else:
                        if option == "6":
                            command = meter[6] + meter_id.strip("J?") + "01"
                        else:
                            if option == "7":
                                command = meter[6] + \
                                    meter_id.strip("J?") + "02"
                            else:
                                if option == "8":
                                    command = meter[6] + \
                                        meter_id.strip("J?") + "06000130"
                                else:
                                    if option == "9":
                                        command = meter[1] + \
                                            meter_id.strip("J?") + "05"
                                    else:
                                        if option == "11":
                                            command = meter[1] + \
                                                meter_id.strip("J?") + "04"
                                        else:
                                            if option == "12":
                                                command = meter[1] + \
                                                    meter_id.strip("J?") + "03"
                                            else:
                                                if option == "2":
                                                    if (rbid == "") & (rbpwd == ""):
                                                        os.system('cls')
                                                        rbid = (input("Route B ID?\r\n>>")).encode(
                                                            'utf-8')
                                                        rbpwd = (input("Route B PWD?\r\n>>")).encode(
                                                            'utf-8')
                                                    command = meter[7] + meter_id.strip(
                                                        "J?") + "2C" + rbid.hex() + rbpwd.hex()
                                                else:
                                                    if option == "99":
                                                        os.system('cls')
                                                        command = input(
                                                            "Input Manual Command: \r\n>>")
                                                        command.replace(
                                                            " ", "")
                                                    else:
                                                        if option == "10":
                                                            os.system('cls')
                                                            print(
                                                                "FW Ver.     Lenght   CRC16")
                                                            print(
                                                                "_______________________________")
                                                            print(
                                                                "V1.20       94648    0x0000A714")
                                                            print(
                                                                "V2.19GT7    94364    0x000064CF")
                                                            print(
                                                                "V2.20       94648    0x000025A3")
                                                            print(
                                                                "V2.20G      94360    0x0000F9A4")
                                                            crc = hex(
                                                                int(input("CRC Lenght? \r\n>>")))
                                                            crc = crc[2:]
                                                            for i in range(0, 8-len(crc)):
                                                                crc = "0" + crc
                                                            command = meter[1] + meter_id.strip(
                                                                "J?") + "08" + crc + "00000000"
                                                        else:
                                                            if option == "13":
                                                                day = input(
                                                                    "Days of Record?\r\n>>")
                                                                command = meter[1] + meter_id.strip("J?") + "02" + hex(
                                                                    int(time.time())-int(day)*86400)[2:] + hex(int(time.time()))[2:]
                                                            else:
                                                                if option == "14":
                                                                    os.system(
                                                                        'cls')
                                                                    print(
                                                                        "Type     Function                                        Option")
                                                                    print(
                                                                        "___________________________________________________________________________")
                                                                    print(
                                                                        "0x00     Daily Meter Diagnostic                          0=Dis / 1=EN")
                                                                    print(
                                                                        "0x01     Sunshine, temperature and humidity  sensor      0=Dis / 1=EN")
                                                                    print(
                                                                        "0x02     Engineering Event Log                           0=Dis / 1=EN")
                                                                    print(
                                                                        "0x03     Load Limit (for 2302H)                          0=Dis / 1=EN")
                                                                    print(
                                                                        "0x04     Load current (for 2302H)                        0 - 255(A)")
                                                                    print(
                                                                        "0x05     Auto-connect time (for 2302H)                   0 - 255(Sec)")
                                                                    print(
                                                                        "0x06     Auto-connect count (for 2302H)                  0 – 255 (times)")
                                                                    print(
                                                                        "0x07     Time to clear the Auto-connect time (for 2302H) 0 – 255 (Min)")
                                                                    print(
                                                                        "0x08     Invert control switch state (for 2302H)         0=NO / 1=NC relay")
                                                                    print(
                                                                        "0x09     PCS Communication Mode                          0=Direct / 1= Delta / 2=Omron")
                                                                    print(
                                                                        "0x80     Interval for data sending                       0 – 255 (Min)")
                                                                    print(
                                                                        "0x81     IoT Platform                                    0:None/G:IIL/X:ESI/A:AWS/M:MS/S:SB")
                                                                    print(
                                                                        "0x82     Daily Diagnostic                                0=Dis/1=Comm only/2=Meter&Comm/3=Meter Control")
                                                                    print(
                                                                        "0x83     Route B Communication Log                       0=Dis / 1=EN")
                                                                    type = input(
                                                                        "Type? \r\n>>")
                                                                    option = input(
                                                                        "Parameter? \r\n>>")
                                                                    command = meter[6] + meter_id.strip("J?") + "03" + '{:02}'.format(
                                                                        str(type)) + '{:02}'.format(str(option)) + "000000000000"
                                                                else:
                                                                    if option == "15":
                                                                        os.system(
                                                                            'cls')
                                                                        address = input(
                                                                            "Move to 1:IIL(219) 2:IIL(129) 3:ESI 4:Manual input?\r\n>>")
                                                                        if (address == "1"):
                                                                            command = meter[6] + meter_id.strip(
                                                                                "J?") + "05" + "14" + "7C33342E39362E3135362E3231397C313838337C000000"
                                                                        else:
                                                                            if (address == "2"):
                                                                                command = meter[6] + meter_id.strip(
                                                                                    "J?") + "05" + "14" + "7C33342E38342E3134332E3132397C313838337C000000"
                                                                            else:
                                                                                if (address == "3"):
                                                                                    command = meter[6] + meter_id.strip(
                                                                                        "J?") + "05" + "14" + "7C35322E3135362E35362E3137307C313838337C000000"
                                                                                else:
                                                                                    if (address == "4"):
                                                                                        ip = input("IP address?\r\n>>").encode(
                                                                                            'utf-8').hex()
                                                                                        port = input("Port?\r\n>>").encode(
                                                                                            'utf-8').hex()
                                                                                        addrlenght = hex(
                                                                                            int((len(ip)+len(port)+6)/2))[2:]
                                                                                        command = meter[6] + meter_id.strip(
                                                                                            "J?") + "05" + addrlenght + "7C" + ip + "7C" + port + "7C"
                                                                    else:
                                                                        if option == "16":
                                                                            os.system(
                                                                                'cls')
                                                                            print(
                                                                                "PCS Monitoring Test")
                                                                            print(
                                                                                "___________________________________________")
                                                                            print(
                                                                                "1. OMRON PCS")
                                                                            print(
                                                                                "2. OMRON2 PCS")
                                                                            print(
                                                                                "3. DELTA PCS")
                                                                            print(
                                                                                "4. Panasonic PCS")
                                                                            pcs = input(
                                                                                "Which PCS? \r\n>>")
                                                                            os.system(
                                                                                'cls')
                                                                            if (pcs == '1'):  # OMRON
                                                                                pcscmd = ["0C02303030303030353031033700000000000000",
                                                                                          "180230303030303031303143323030304130303030303103320000000000000000000000",
                                                                                          "180230303030303031303143333030303030303030303103420000000000000000000000",
                                                                                          "180230303030303031303143333030303230303030303103400000000000000000000000",
                                                                                          "0C02303030303030363031033400000000000000",
                                                                                          "180230303030303031303143323030303030303030303103430000000000000000000000",
                                                                                          "180230303030303031303143323030303130303030303103420000000000000000000000",
                                                                                          "180230303030303031303143323030303430303030303103470000000000000000000000",
                                                                                          "180230303030303031303143323030303530303030303103460000000000000000000000",
                                                                                          "180230303030303031303143363031303130303030303103470000000000000000000000",
                                                                                          "180230303030303031303134303030303030303030303103360000000000000000000000",
                                                                                          "180230303030303031303143313030303630303030303103460000000000000000000000"]
                                                                            # OMRON 2
                                                                            if (pcs == '2'):
                                                                                pcscmd = ["180230303030303031303134303030303330303030303103350000000000000000000000",
                                                                                          "1802303030303030313031343030303038303030303031033E0000000000000000000000",
                                                                                          "180230303030303031303143323031303130303030303103430000000000000000000000",
                                                                                          "180230303030303031303143323031303230303030303103400000000000000000000000",
                                                                                          "180230303030303031303143323031303430303030303103460000000000000000000000"]
                                                                            if (pcs == '3'):  # DELTA
                                                                                pcscmd = ["080104C03E000CADC30000000000000000000000",
                                                                                          "080103CDBF0006CA800000000000000000000000",
                                                                                          "08010451FE000140C60000000000000000000000",
                                                                                          "080104AFFF000A61290000000000000000000000",
                                                                                          "080104B0120012F6C20000000000000000000000",
                                                                                          "080104C05F0003BC190000000000000000000000",
                                                                                          "080103833C00016D820000000000000000000000",
                                                                                          "080103BC1D0004F19F0000000000000000000000",
                                                                                          "080104F002005AE2F10000000000000000000000",
                                                                                          "080103634200013A5A0000000000000000000000",
                                                                                          "080104CFFF00267EF40000000000000000000000",
                                                                                          "080104BFFF001E65E60000000000000000000000"]
                                                                            # Panasonic
                                                                            if (pcs == '4'):
                                                                                pcscmd = ["08010300230003F4010000000000000000000000",
                                                                                          "0801030030000985C30000000000000000000000",
                                                                                          "08010300570004F5D90000000000000000000000",
                                                                                          "080103001E0056A5F20000000000000000000000"]
                                                                            for i in range(0, len(pcscmd), 1):
                                                                                if (pcs == '1'):
                                                                                    command = meter[8] + meter_id.strip(
                                                                                        "J?") + "0003020702" + pcscmd[i]
                                                                                if (pcs == '2'):
                                                                                    command = meter[8] + meter_id.strip(
                                                                                        "J?") + "0003020702" + pcscmd[i]
                                                                                if (pcs == '3'):
                                                                                    command = meter[8] + meter_id.strip(
                                                                                        "J?") + "0004000801" + pcscmd[i]
                                                                                if (pcs == '4'):
                                                                                    command = meter[8] + meter_id.strip(
                                                                                        "J?") + "0003020801" + pcscmd[i]
                                                                                payload = bytes.fromhex(
                                                                                    command)
                                                                                decipher = AES.new(
                                                                                    key=hexkey, mode=AES.MODE_CBC, iv=hexiv)
                                                                                enc = decipher.encrypt(
                                                                                    payload)
                                                                                print(
                                                                                    "Command ", i+1, ": ", command)
                                                                                # print("Message...:" + enc.hex())
                                                                                print(
                                                                                    "Wait 10sec...")
                                                                                # 要發布的主題和內容
                                                                                client.connect(
                                                                                    server_ip, 1883, 600)
                                                                                client.publish(
                                                                                    topic, enc)
                                                                                client.disconnect()
                                                                                time.sleep(
                                                                                    10)
                                                                            command = ""
                                                                        else:
                                                                            if option == "18":
                                                                                os.system(
                                                                                    'cls')
                                                                                json = input(
                                                                                    "JSON? (In single line) \r\n>>")
                                                                                command = json.encode(
                                                                                    'utf-8').hex()
                                                                            else:
                                                                                if option == "19":
                                                                                    os.system(
                                                                                        'cls')
                                                                                    exkey = input(
                                                                                        "Input Data Key\r\n>>")
                                                                                    print(
                                                                                        "1. Send Data Key\n")
                                                                                    print(
                                                                                        "2. Send Successful ACK\n")
                                                                                    option = input(
                                                                                        "Which Step?\r\n>>")
                                                                                    if option == "1":
                                                                                        command = meter[0] + meter_id.strip(
                                                                                            "J?") + "00" + exkey.encode('utf-8').hex()
                                                                                    else:
                                                                                        if option == "2":
                                                                                            command = meter[0] + meter_id.strip(
                                                                                                "J?") + "02"
                                                                                        else:
                                                                                            print(
                                                                                                "Wrong Input")
                                                                                            time.sleep(
                                                                                                1)
                                                                                else:
                                                                                    print(
                                                                                        "Wrong Input")
                                                                                    command = ""
    # command = "c14a200000406f010000000000000000"
    # command = input("Hex Command?\r\n>>")
    if (command != ""):
        while (len(command) % 32 != 0):
            command += "0"
        payload = bytes.fromhex(command)
        decipher = AES.new(key=hexkey, mode=AES.MODE_CBC, iv=hexiv)
        enc = decipher.encrypt(payload)
        print("Message...:" + enc.hex())
        # 要發布的主題和內容
        client.connect(server_ip, 1883, 600)
        client.publish(topic, enc)
        client.disconnect()
    time.sleep(1)
