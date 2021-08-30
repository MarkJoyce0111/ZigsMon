'''FUNCTIONS'''
import sys, os
import zigbee
from datetime import datetime, timedelta
from zigbee import *
from socket import *
from time import sleep
import binascii
from zigsClass import SimpleDescriptorResponse
from zigsType import *
import json
import multiprocessing
sys.path.append("importlibs.zip")
import requests

#import requests.packages.urllib3
#requests.packages.urllib3.disable_warnings()
#import certifi
import urllib3
#from cryptography import certificate_transparency
#from OpenSSL import crypto
#from cryptography.x509 import certificate_transparency
#import urllib3.contrib.pyopenssl
#urllib3.contrib.pyopenssl.inject_into_urllib3()
urllib3.disable_warnings()
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs='/etc/ssl/certs/ca-certificates.crt')

#  Globals. Not really needed.
TRANS_NUMBER = 0 #Dev Variable. A assignable number to each packet.
ZONE_NUMBER = 0 #Dev Variable. A assignable number to each end device.
rec_timeout = 20 # Message Time Out.

######################################################
##  Get the temperature from motion and door sensor ##
##  Caution! May miss other incomming sensor data.  ##
##  It rejects messages from other devices whilst   ##
##  waiting for device temp message.                ##
                                                    ##
GET_IAS_TEMP = False                                ##
######################################################

#  HTTPS
headers = {'content-type': 'application/json'}
url = 'https://gerimonapi.azurewebsites.net/api/geridatas'



def check_info_file(node_info_dict, path):
    add_list = {}
    node_info_copy = node_info_dict.copy() # Make a copy of the Node List Dictionary (Not a Pointer!)

    # see if the file exists
    file_exists = os.path.exists(path)

    if file_exists:
        print "FILE EXISTS!"
        counter = 0
        # Open file and extract data
        f = open(path, "r")
        data = f.read()
        f.close()
        file_node_info = json.loads(data)  # We convert the JSON object to a Dictionary

    # Delete existing nodes from the list copy; thus leaving the ones that are not on file; ie new devices.
        for i in file_node_info:
            for j in node_info_copy.keys():
                if file_node_info[i]['long_address'] == node_info_copy[j]['long_address']:
                    del node_info_copy[j]

    # Are there any new devices?; Does node list have an entry / entries
        if bool(node_info_copy):
            print "New devices"
            for k in node_info_copy:
                print node_info_copy[k]['long_address']

        # Extract the address from the current connected LIST.
            counter = 0
            for i in node_info_copy:
                add_list[counter] = {}
                add_list[counter] = node_info_copy[i]  # Each entry
                counter += 1

                print "\n\nAdding the new node from node_list_copy\n\n", add_list, "\n\n"

        #  Recopy the nodes on file, using the same counter.
            for i in file_node_info.keys():
                add_list.update({counter:{}}) # Tricky Aye.
                add_list[counter] = file_node_info[str(i)]
                counter += 1

            print "\n\nAdding the saved nodes from file_node_list\n\n", add_list, "\n\n"
            dump_back_nodes = json.dumps(add_list, indent=4) # We convert the dictionary to JSON format
            # We write the JSON object to back to file so the new device can have its friendly_name changed.
            f = open(path,"w")
            f.write(dump_back_nodes)
            f.close()
            print "All Done"
            return json.loads(dump_back_nodes) # Convert to Dictionary before returning.

        else:
         # No New Devices Found that ane not in the node file already. Return the node list from the file.
            print "NO NEW DEVICES"
            return file_node_info  # file_node_info is a Dictionary already!.

    else: # File does not exist | First Run OR File Deleted - Takes current node list and saves it.
        print "FILE DOES NOT EXIST"
        # Converts Dictionary to JSON
        file_node_info = json.dumps(node_info_copy, indent=4)

        # We write the JSON object to file
        f = open(path,"w")
        f.write(file_node_info)
        f.close()

        return json.loads(file_node_info) # We convert the JSON object to a Dictionary before returning it.


# Check the node file, load friendly names, and add any new devices.
# Takes in current node list and compares it to saved nodes.
# Edit dict.json "friendly_name" and change to an area location. eg "Kitchen Stove".
def check_file(node_list, path):
    addList = {}
    node_list_copy = node_list.copy() # Make a copy of the Node List Dictionary (Not a Pointer!)

    # see if the file exists
    file_exists = os.path.exists(path)

    if file_exists:
        # Open file and extract data
        f = open(path, "r")
        data = f.read()
        f.close()
        file_node_list = json.loads(data)  # We convert the JSON object to a Dictionary

    # Delete existing nodes from the list copy; thus leaving the ones that are not on file; ie new devices.
        for i in range(len(file_node_list)):
            for j in node_list_copy.keys():
                if file_node_list[str(i)]['address'] == node_list_copy[j][0]:
                    del node_list_copy[j]

    # Are there any new devices?; Does node list have an entry / entries
        if bool(node_list_copy):
            print "New devices"
            for k in node_list_copy:
                print node_list_copy[k][0]

        # Extract the address from the current connected LIST.
            counter = 0
            for i in node_list_copy:
                addList[counter] = {}
                addList[counter]['address'] = node_list_copy[i][0]  # Long Address
                addList[counter]['friendly_name'] = node_list_copy[i][0]  #  Fill this with the Long address at this point
                counter += 1

                print "\n\nAdding the new node from node_list_copy\n\n", addList, "\n\n"

        #  Recopy the nodes on file, using the same counter.
            for i in file_node_list:
                addList.update({counter:{}}) # Tricky Aye.
                addList[counter]['address'] = file_node_list[str(i)]['address']
                addList[counter]['friendly_name'] = file_node_list[str(i)]['friendly_name']
                counter += 1

            print "\n\nAdding the saved nodes from file_node_list\n\n", addList, "\n\n"
            print "All Done"

            dump_back_nodes = json.dumps(addList, indent=4) # We convert the dictionary to JSON format

            # We write the JSON object to back to file so the new device can have its friendly_name changed.
            f = open(path,"w")
            f.write(dump_back_nodes)
            f.close()
            return json.loads(dump_back_nodes) # Convert to dictionary

        else:
         # No New Devices Found that ane not in the node file already. Return the node list from the file.
            return file_node_list # Already a dictionary

    else: # File does not exist | First Run OR File Deleted - Takes current node list and saves it.
        for i in range(len(node_list_copy)):
            addList[i] = {}
            addList[i]['address'] = node_list_copy[i][0]
            addList[i]['friendly_name'] = node_list_copy[i][0]

        # Converts Dictionary to JSON
        file_node_list = json.dumps(addList, indent=4)

        # We write the JSON object to file
        f = open(path,"w")
        f.write(file_node_list)
        f.close()
        #file_node_list_dict = json.loads(file_node_list) # Covert to Dict
        return json.loads(file_node_list)


# Identify end Device. Causes LED on device to flash.
# time on in seconds up to 0xFF (255).
def identify_end_device(address_64, time_on):
    print "Identify"
    Destination = (address_64, 0x01, 0x0104, 0x0003)
    payLoad, addrMeta = send_it(Destination, 0x01, Cluster_Specific + chr(0xAA) + chr(0x00) + chr(0x00) + chr(time_on), 100)
    #print_payload(addrMeta, payLoad)


# End the identity process.
# Stop the flashing of the LED on end device.
def end_identify_end_device(address_64):
    print "End Identify"
    Destination = (address_64, 0x01, 0x0104, 0x0003)
    payLoad, addrMeta = send_it(Destination, 0x01, Cluster_Specific + chr(0xAA) + chr(0x00) + chr(0x00) + chr(0x00), 100)
    #print_payload(addrMeta, payLoad)


# Get the temperature from end device. If supported! Door Sensors and Motion Detectors do.
# ToDo Not Used: Delete.
def get_temp(address_64):
    Destination = (address_64, 0x01, 0x0104, 0x0402) # destination, DestEndpoint, message, bufferLength, cluster)
    payLoad, addrMeta = send_it(Destination, 0x01, Entire_Profile + chr(0xAA) + chr(Read_Attributes) + chr(0x0000) + chr(0x0000), 100)
    return payLoad, addrMeta


# Get temperature receive loop from inside Main receive loop.
def receive_loop_get_temperature(class_name, address_64):
    # Reply Payload[6] should = 0x29 (41) when a  HA (0x0104), to measurement and sensing cluster 0x0402 is performed.
    destination = (address_64, 0x01, 0x0104, 0x0402)
    address_check = address_64
    while True:
        message = Entire_Profile + chr(0xAA) + chr(Read_Attributes) + chr(0x0000) + chr(0x0000)
        class_name.sendto(message, 0, destination)
        payLoad, addrMeta = class_name.recvfrom(100)

        if address_check == addrMeta[0] and ord(payLoad[6]) == 0x29:  # compare return message address with sending address. Eg a message from another device may appear so filter it.
            temperature = float((ord(payLoad[8]) << 8 | ord(payLoad[7]))) / 100
            return payLoad, addrMeta, temperature

        else:
            print "Error, receive loop get temperature, Possibly different device message; ie motion detected / door opened!"
            print "Address Detail", addrMeta
            print "Resending"

# Send payload to database.
def send_to_database(payload_out):
    payload_JSON = json.dumps(payload_out) # Convert Dictionary to JSON
    return_message = requests.post(url, payload_JSON, headers = headers) # Send Payload

    if return_message.status_code == 201: # Success
        print "Message Success: ", return_message
        returnJSON = return_message.json() #Can convert class object to json.
        print "Return Message: "
        print json.dumps(returnJSON, indent=4, sort_keys=True)

    else: # Failure
        print "Something went wrong ", return_message
        print "Return Message: ", return_message.text
        # ToDo Add Logging Here!

# NOT USED: SEE commissionDevices.py and zigsMon.py -> receive_loop2(....). Used in Dev.
# Receive Loop, Development Only.
# Loopy Message Handler, processes incoming messages -> needs work! Nah ALL DONE!
def receive_Loop(ias_node_dictionary, file_node_info_dict,  environment_info_dict, file_node_list):

    sd = socket(AF_ZIGBEE, SOCK_DGRAM, XBS_PROT_TRANSPORT)
    sd.bind(("", 1, 0, 0))
    print "the IAS node_dictionary is ", ias_node_dictionary
    print "the Enviroment node_dictionary is ", environment_info_dict, "\n"
    while True:
        inDict = False
        InWhiteList = False
        friendly_name = ""
        '''    revcfrom return data   http://cms.digi.com/resources/documentation/digidocs/90001537/#references/r_xbee_extensions_to_python_socket.htm%3FTocPath%3DWorking%2520with%2520Zigbee%7C_____26
        
                          [0]          [1]        [2]          [3]                [4]               [5]
        src_addr = {Address String, Endpoint, Profile ID, Source Cluster ID, options bit mask, transmission_id }
        '''
        payload, src_addr = sd.recvfrom(100) #ToDo
        print "*" * 20, "Received", "*" * 20
        address = src_addr[0]
        address2 = address.strip('!][')
        compare_address = address2 + "!"
        #print "From Address: ", address
        #print "From Address Data: ", src_addr
        print "Address String = ", src_addr[0]
        print "Endpoint = ", src_addr[1]
        print "Profile ID = ", Profile_Type[src_addr[2]]
        print "Cluster ID = ", Member_Cluster[src_addr[3]]

        print_payload(src_addr, payload)

        # IF the payload is from an IAS Device (0x0500) under Home Automation process here.
        if src_addr[2] == Home_Automation_Cluster_ID  and src_addr[3] == IAS_Zone:
            # Double check the message is a Read_Reporting_Configuration_Response
            if ord(payload[2]) == Message_Success and ord(payload[0]) == Read_Reporting_Configuration_Response:

                for x in range(len(ias_node_dictionary)):
                    if ias_node_dictionary[x][0] == address:
                        # print node_dictionary[x][0], "is equal to", address
                        node_dict_data_out_long_address = ias_node_dictionary[x][0]
                        node_dict_data_out_short_add = ias_node_dictionary[x][2]
                        #node_info_dict_data_out = node_info_dict[x] #                  Todo Fix this so it uses file node info
                        inDict = True
                        break

                # JSon loads!
                #  Get the Node info.
                for x in range(len(file_node_info_dict)):
                    if file_node_info_dict[str(x)]['long_address'] == compare_address:
                        node_info_dict_data_out = file_node_info_dict[str(x)]
                        break

                #print file_node_list
                if inDict == False:
                    # Node in the node dict check routers by comparing whitelist in file.
                    for x in range(len(file_node_list)):
                        if file_node_list[str(x)]['address'] == address:
                            # print node_dictionary[x][0], "is equal to", address
                            node_dict_data_out_long_address = file_node_list[str(x)]['address']
                            node_dict_data_out_short_add = None # file_node_list[x][2]
                            friendly_name = file_node_list[str(x)]['friendly_name']
                            InWhiteList = True
                            break


                #IF IAS device is in the node node dictionary.
                if inDict == True:
                    print "IN DICT !!!!"
                    #  Get IAS device Temperature
                    if GET_IAS_TEMP == True:
                        p, a, temperature = receive_loop_get_temperature(sd, address)

                # Get device Friendly Name
                    for x in file_node_list.keys():
                        if file_node_list[x]['address'] == node_dict_data_out_long_address:
                            friendly_name = file_node_list[x]['friendly_name']
                            break
                    # Get some data from the zone status bit map - Section 8.2.2.2.1.3 ZoneStatus Attribute chapter 8 page 3
                    zone_status_attribute = ord(payload[4]) << 8 | ord(payload[3])
                    state = zone_status_attribute & 0b00000001  # using AND bit mask, bit 1
                    battery = zone_status_attribute & 0b00000100  # using AND bit mask, bit 3
                    # Get the Zone ID
                    zone_id = ord(payload[6])

                    if state == 1:
                        state_out = "OPEN"
                    elif state == 0:
                        state_out = "CLOSED"
                    if battery == 0:
                        battery_out = "OK"
                    else:
                        battery_out = "LOW"
                    #for index, byte in enumerate(payload):
                        #print "payload[%d] = %s (%d)" % (index, hex(ord(byte)), ord(byte))

                    #  Construct payload.
                    if GET_IAS_TEMP == True:
                        payload_out = {
                            "timestamp": get_time_stamp(),
                            "longaddress": str(node_dict_data_out_long_address),
                            "shortaddress": str(node_dict_data_out_short_add),
                            "devicefriendlyname": friendly_name,
                            "devicetemperature": temperature,
                            "devicetype": Device_Type[node_info_dict_data_out["device_type"]],
                            "devicestate": state_out,
                            "zoneid": zone_id,
                            "batterystate": battery_out }
                    else:
                        payload_out = {
                            "timestamp": get_time_stamp(),
                            "longaddress": str(node_dict_data_out_long_address),
                            "shortaddress": str(node_dict_data_out_short_add),
                            "devicefriendlyname": friendly_name,
                            "devicetemperature": 0,
                            "devicetype": Device_Type[node_info_dict_data_out["device_type"]],
                            "devicestate": state_out,
                            "zoneid": zone_id,
                            "batterystate": battery_out }


                    #  Send Payload
                    payload_JSON = json.dumps(payload_out) # Convert Dictionary to JSON
                    print "Sending Payload to: ", url
                    return_message = requests.post(url, payload_JSON, headers = headers) # Send Payload

                    if return_message.status_code == 201: # Success
                        print "Message Success: ", return_message
                        returnJSON = return_message.json() #Can convert class object to json.
                        print "Return Message: "
                        print json.dumps(returnJSON, indent=4, sort_keys=True)

                    else: # Failure
                        print "Something went wrong ", return_message
                        print "Return Message: ", return_message.text
                        # ToDo Add Logging Here!

                    print "*" * 50, "\n"

                # Must be from a router!
                elif InWhiteList == True:
                    print "IN WHITE LIST !!!!"
                    #  Get IAS device Temperature
                    if GET_IAS_TEMP == True:
                        p, a, temperature = receive_loop_get_temperature(sd, address)

                    # Get some data from the zone status bit map - Section 8.2.2.2.1.3 ZoneStatus Attribute chapter 8 page 3
                    zone_status_attribute = ord(payload[4]) << 8 | ord(payload[3])
                    state = zone_status_attribute & 0b00000001  # using AND bit mask, bit 1
                    battery = zone_status_attribute & 0b00000100  # using AND bit mask, bit 3
                    # Get the Zone ID
                    zone_id = ord(payload[6])

                    if state == 1:
                        state_out = "OPEN"
                    elif state == 0:
                        state_out = "CLOSED"
                    if battery == 0:
                        battery_out = "OK"
                    else:
                        battery_out = "LOW"
                    #for index, byte in enumerate(payload):
                        #print "payload[%d] = %s (%d)" % (index, hex(ord(byte)), ord(byte))

                    #  Construct payload.
                    if GET_IAS_TEMP == True:
                        payload_out = {
                            "timestamp": get_time_stamp(),
                            "longaddress": str(node_dict_data_out_long_address),
                            "shortaddress": str(node_dict_data_out_short_add),
                            "devicefriendlyname": friendly_name,
                            "devicetemperature": temperature,
                            "devicetype": Device_Type[node_info_dict_data_out["device_type"]],
                            "devicestate": state_out,
                            "zoneid": zone_id,
                            "batterystate": battery_out }
                    else:
                        payload_out = {
                            "timestamp": get_time_stamp(),
                            "longaddress": str(node_dict_data_out_long_address),
                            "shortaddress": str(node_dict_data_out_short_add),
                            "devicefriendlyname": friendly_name,
                            "devicetemperature": 0,
                            "devicetype": Device_Type[node_info_dict_data_out["device_type"]],
                            "devicestate": state_out,
                            "zoneid": zone_id,
                            "batterystate": battery_out }

                    #  Send Payload
                    payload_JSON = json.dumps(payload_out) # Convert Dictionary to JSON
                    print "Sending Payload to: ", url
                    p1 = multiprocessing.Process(target=send_to_database, args=(payload_out,))
                    p1.start()
                    p1.join()
                    print "*" * 50, "\n"

                # No Record of 64 bit address
                else:
                    print "Device is not in Dictionary, no idea how that works. Attack?" # ToDo add logging here.

        # ToDo make this section work for all relative humidity and temperature measurements.
        # ToDo OR make some kind of commissioning system, ie push button, OR menu based.
        #  Message from LUMI Temperature and Humidity sensor
        elif src_addr[2] == Home_Automation_Cluster_ID and src_addr[3] == Relative_Humidity_Measurement or src_addr[3] == Temperature_Measurement:
            address = src_addr[0]
            for x in environment_info_dict.keys(): # Iterate through Dictionary.
                if environment_info_dict[x]['long_address'] == address:
                    # print node_dictionary[x][0], "is equal to", address
                    node_dict_data_out_long_address = environment_info_dict[x]['long_address']
                    node_dict_data_out_short_add = environment_info_dict[x]['long_address']
                    node_info_dict_data_out = environment_info_dict[x]
                    inDict = True
                    break

            if inDict == True:  # If device is in device dictionary process,  otherwise reject message.
                for x in file_node_list.keys():
                        if file_node_list[x]['address'] == node_dict_data_out_long_address:
                            friendly_name = file_node_list[x]['friendly_name']
                            break

                if ord(payload[0]) == 0x18 and (ord(payload[5]) == 0x29 or ord(payload[5]) == 0x21):
                    try:
                        if src_addr[3] == Relative_Humidity_Measurement: # Received a humidity measurement
                            print "-" * 10
                            print"Relative Humidity = ", float((ord(payload[7]) << 8 | ord(payload[6]))) / 100
                            print "-" * 10
                            # Construct Environment Sensor Payload | Humidity
                            payload_out = {
                                "timestamp": get_time_stamp(),
                                "longaddress": str(node_dict_data_out_long_address),
                                "shortaddress": str(node_dict_data_out_short_add),
                                "devicefriendlyname": friendly_name,
                                "devicehumidity": float((ord(payload[7]) << 8 | ord(payload[6]))) / 100,
                                "devicetype": "Environment sensor",
                                }

                            #  Send PAYLOAD OUT!

                            print "Sending Payload to: ", url
                            p1 = multiprocessing.Process(target=send_to_database, args=(payload_out,))
                            p1.start()
                            p1.join()
                            print "*" * 50, "\n"

                        elif src_addr[3] == Temperature_Measurement: # Received Temperature measurement
                            print "-" * 10
                            print "Temperature = ", float((ord(payload[7]) << 8 | ord(payload[6]))) / 100
                            print "-" * 10

                            # Construct Environment Sensor Payload | Temperature
                            payload_out = {
                                "timestamp": get_time_stamp(),
                                "longaddress": str(node_dict_data_out_long_address),
                                "shortaddress": str(node_dict_data_out_short_add),
                                "devicefriendlyname": friendly_name,
                                "devicetemperature": float((ord(payload[7]) << 8 | ord(payload[6]))) / 100,
                                "devicetype": "Environment sensor",
                                }

                            #  Send PAYLOAD OUT!
                            print "Sending Payload to: ", url
                            p1 = multiprocessing.Process(target=send_to_database, args=(payload_out,))
                            p1.start()
                            p1.join()
                            print "*" * 50, "\n"

                    except:

                        print "Message Error"
                        print payload
                        c = len(payload) - 1
                        print "ErrNum = ", payload[c]

    # sd.close()


# Constructs 64 bit device friendly address.
def construct_address(address_64):
    address_check = "[" + address_64
    address_check = address_check.replace("!", "]")
    address_check += "!"
    return address_check


# Get Zone Type Attribute.
def get_zone_type_attribute(address_64, trans_number, retries):
    address_check = construct_address(address_64)
    print "\n\rZone Type Request - HA profile, 0x00000"
    Destination = (address_64, 0x01, 0x0104, 0x0500)
    #Destination2 = (Destination, 0x00, 0x0000, 0x0004)

    for x in range(retries):
        payLoad, addrMeta = send_it(Destination, 0x01, chr(0x00) + chr(trans_number) + chr(0x0) + chr(0x01) + chr(0x00), 100)
        try:
            temp = addrMeta[0]
            if address_check == temp and ord(payLoad[0]) == 0x18:  # compare return message address with sending address. Eg a message from another device may appear so filter it.
                return payLoad, addrMeta

        except TypeError:
            print "Message returned false: Retry"
            print addrMeta
            print payLoad
            pass
        sleep(1)

    return False, False


# Get Zone state attribute
def get_zone_state_attribute(address_64, trans_number, retries):
    address_check = construct_address(address_64)
    print "\n\rZone State Request - HA profile, 0x00000: ", address_64
    Destination = (address_64, 0x01, 0x0104, 0x0500)
    #Destination2 = (Destination, 0x00, 0x0000, 0x0004)

    for x in range(retries):
        payLoad, addrMeta = send_it(Destination, 0x01, chr(0x00) + chr(trans_number) + chr(0x00) + chr(0x00) + chr(0x00), 100)
        temp = addrMeta[0]
        if address_check == temp and ord(payLoad[0]) == 0x18:  # compare return message address with sending address. Eg a message from another device may appear so filter it.
            return payLoad, addrMeta
        sleep(1)
    return False, False


# Get Intruder Alarm System (IAS) devices current zone ID
def get_zone_id(address_64, trans_number, retries):
    address_check = construct_address(address_64)
    Destination = (address_64, 0x01, 0x0104, 0x0500)
    #(Destination, 0x01, "\x00"+"\xAA"+"\x00"+"\x11\x00", 100, 0x0500)

    for x in range(retries):
        payLoad, addrMeta = send_it(Destination, 0x01, "\x00" + chr(trans_number) + "\x00" + "\x11\x00", 100)
        temp = addrMeta[0]
        if address_check == temp and ord(payLoad[0]) == 0x18:  # compare return message address with sending address. Eg a message from another device may appear so filter it.
            return payLoad, addrMeta
        sleep(1)
    return False, False


# Enrol Intruder Alarm System Device
def enrol_device(address_64, LEcoordinator_address, transNumber, retries):
    address_check = construct_address(address_64)

    Destination = (address_64, 0x01, Home_Automation_Cluster_ID, IAS_Zone)
    for x in range(retries):
        # DestinationTuple|DestEndPoint*ZCLFrameControl|TransNumber|Cluster Command|Zone Settings Attribute|DataType|CoordinatorAddress*BufferSize|DestClusterID
        payLoad, addrMeta = send_it(Destination, 0x01, Entire_Profile + chr(transNumber) + chr(Write_Attributes) + IAS_CIE_Address + EUI64 + LEcoordinator_address, 100)
        temp = addrMeta[0]
        if address_check == temp and ord(payLoad[0]) == 0x18:  # compare return message address with sending address. Eg a message from another device may appear so filter it.
            return payLoad, addrMeta
        sleep(1)
    return False, False


# Get current zone ID from device.
def read_zone_id(address_64, transNumber, retries):
    address_check = construct_address(address_64)

    print "\n\rRead ZoneID - 0x0000 - State"
    Destination = (address_64, 0x01, Home_Automation_Cluster_ID, IAS_Zone)
    for x in range(retries):
        payLoad, addrMeta = send_it(Destination, 0x01, "\x00" + chr(transNumber) + "\x00" + "\x00\x00", 100)
        temp = addrMeta[0]
        if address_check == temp and ord(payLoad[0]) == 0x18:  # compare return message address with sending address. Eg a message from another device may appear so filter it.
            return  payLoad, addrMeta
        sleep(1)
    return False, False


# Send an enroll response to end node. Expects no reply.
def send_enrol_response(address_64, zoneNumber):
    print "\n\rSend Zone Enrol Response - "
    destination = (address_64, 0x01, Home_Automation_Cluster_ID, IAS_Zone)
    # DestinationTuple|DestEndPoint*FrameControl|TransNumber|CommandID?????|Enroll response code|New ZoneId
    send_no_reply(destination, 0x01, Cluster_Specific + chr(auto_transaction_number()) + Zone_Enroll_Response + Enroll_Success + chr(zoneNumber), IAS_Zone)


# TODO Possibly tidy up this function and add try and except instead of returning FALSE from 'get zone type' and 'get zone state' functions.
# Enrol IAS Zone type device. Iterates through the node dictionary for IAS devices. Then enrols them.
# Devices are sent the coordinators address in byte array and little endian format. This tells them where to send their state change notifications
# Devices are then sent a zone number, from this point they start sending state change notifications.
def ias_device_enrol(node_dictionary, node_info_dict, coordinator_address):
    #  Check IAS zone devices zone state, type and status -> 8.2.2.2.1 file:///C:/Users/Mark/Downloads/07-5123-06-zigbee-cluster-library-specification%20(4).pdf
    # enrol whats not enrolled
    #print"NODE DICT"
    #print node_dictionary

    for i in range(len(node_dictionary)):  # Iterate through end device dictionary.
        #  Check to see if any devices are IAS zone devices, if so enrol and set their zones.
     #   print "NODE INFO DICT "
     #   print json.dumps(node_info_dict[i], indent=4)
     #   print "\n\r"

        if '0x500' in node_info_dict[i]['input_cluster_list']:  # 0x0500 = IAS Zone Device.
            if '0x402' in node_info_dict[i]['input_cluster_list']:
                node_info_dict[i]["temperature_measurement"] = True
            print "Found IAS Device"
            print "Zone Type Request"
            address_64, address_16 = get_addresses(node_dictionary, i)  # get the device addresses from the node dictionary
            payLoad, addrMeta = get_zone_type_attribute(address_64, auto_transaction_number(), 5)  # get zone type attribute

            if payLoad == False:
                print "Receive ERROR, <- get Zone Attribute - Lengthen Retries!"
                print "TO DO - Remove entry from node_list and node_info_dict"
            else:

                # Set device type in the node_info_dictionary
                node_info_dict[i]['device_type'] = ord(payLoad[8]) << 8 | ord(payLoad[7])
                print "Device Type = ", Device_Type[node_info_dict[i]['device_type']]

                # Get Zone Device State
                payLoad, addrMeta = get_zone_state_attribute(address_64, auto_transaction_number(), 5)  #
                #print_payload(addrMeta, payLoad)

                if payLoad == False:
                    print "Receive ERROR, <- get Zone Attribute - Lengthen Retries!"
                    print "TO DO - Remove entry from node_list and node_info_dict"
                else:

                    if ord(payLoad[3]) == 0:
                        print "SUCCESS"
                    else:
                        print "Message Failure"
                        print "*" * 30
                        print payLoad
                    if ord(payLoad[7]) == 1:  # If device is enrolled
                        print "Device Enrolled!"
                        # Update Node Dictionary data
                        node_info_dict[i]["enrolled"] = True
                        node_info_dict[i]["ias_device"] = True

                        # Get Zone ID
                        payLoad, addrMeta = get_zone_id(address_64, auto_transaction_number(), 5)
                        if payLoad == False:
                            print "Receive ERROR, <- get Zone Attribute - Lengthen Retries!"
                            print "TO DO - Remove entry from node_list and node_info_dict"
                        else:
                            if ord(payLoad[2]) == 1:
                                print "Zone ID Request SUCCESS"
                                node_info_dict[i]["zoneID"] = payLoad[7]
                                # print_payload(addrMeta, payLoad)             # TODO <------------ REMOVED PAYLOAD FEEDBACK!
                            else:
                                print "ERROR sending Zone Request"
                    else:
                        # Device is not enrolled
                        print "Device Not Enrolled \n\rEnrolling Device"
                        #  Enroll the device
                        payLoad, addrMeta =  enrol_device(address_64, coordinator_address, auto_transaction_number(), 5)
                        if payLoad == False:
                            print "Receive ERROR, <- get Zone Attribute - Lengthen Retries!"
                            print "TO DO - Remove entry from node_list and node_info_dict"
                        else:
                            print "Read Zone ID"
                            #  Read Zone ID
                            payLoad, addrMeta = get_zone_id(address_64, auto_transaction_number(), 5)
                            if payLoad == False:
                                print "Receive ERROR, <- get Zone Attribute - Lengthen Retries!"
                                print "TO DO - Remove entry from node_list and node_info_dict"
                            else:
                                #  Send Zone Enrol Response
                                temp = auto_zone_number()
                                node_info_dict[i]["ZoneNumber"] = temp
                                send_enrol_response(address_64, temp) #  NO REPLY EXPECTED!

                                print "Read Zone ID"
                                #  Read Zone ID
                                payLoad, addrMeta = get_zone_id(address_64, auto_transaction_number(), 5)

                                if payLoad == False:
                                    print "Receive ERROR, <- get Zone Attribute - Lengthen Retries!"
                                    print "TO DO - Remove entry from node_list and node_info_dict"
                                else:
                                    payLoad, addrMeta = get_zone_state_attribute(address_64, auto_transaction_number(), 5)
                                    if payLoad == False:
                                        print "Receive ERROR, <- get Zone Attribute - Lengthen Retries!"
                                        print "TO DO - Remove entry from node_list and node_info_dict"
                                    else:
                                        if ord(payLoad[7]) == 1:
                                            print "Device Enrolled"
                                            # Update Node Dictionary data
                                            node_info_dict[i]["enrolled"] = True
                                            node_info_dict[i]["ias_device"] = True
                                            # Get the zoneID
                                            payLoad, addrMeta = get_zone_id(address_64, auto_transaction_number(), 5)
                                            if payLoad == False:
                                                print "Receive ERROR, <- get Zone Attribute - Lengthen Retries!"
                                                print "TO DO - Remove entry from node_list and node_info_dict"
                                            else:
                                                #  Set the Zone ID dictionary element
                                                if ord(payLoad[2]) == 1:
                                                    print "Zone ID Request SUCCESS"
                                                    node_info_dict[i]["zoneID"] = payLoad[7]

    return node_info_dict


# Not Working
def ias_device_unenrol(node_dictionary, node_info_dict):
    for i in range(len(node_dictionary)):  # Iterate through end device dictionary.
        #  Check to see if any devices are IAS zone devices, if so enrol and set their zones.
        if '0x500' in node_info_dict[i]['input_cluster_list']:  # 0x0500 = IAS Zone Device.
            print"Found IAS Device"
            address_64, address_16 = get_addresses(node_dictionary, i)  # get the device addresses from the node dictionary
        #  Enroll the device
            payLoad, addrMeta = enrol_device(address_64, "\x00\x00\x00\x00\x00\x00\x00\x00", auto_transaction_number(), 5)
            if payLoad == False:

                print "Receive ERROR, <- get Zone Attribute - Lengthen Retries!"
                print "TO DO - Remove entry from node_list and node_info_dict"
            else:
                print "Device un-enrolled, check them"
                print_payload(addrMeta, payLoad)
                #  sleep(1)
                # Get Zone Device State
                print "State!"
                payLoad, addrMeta = get_zone_state_attribute(address_64, auto_transaction_number(), 5)  #
                print_payload(addrMeta, payLoad)
                print "Read Zone ID"
                #  Read Zone ID
                payLoad, addrMeta = get_zone_id(address_64, auto_transaction_number(), 5)

                if payLoad == False:
                    print "Receive ERROR, <- get Zone Attribute - Lengthen Retries!"
                    print "TO DO - Remove entry from node_list and node_info_dict"
                else:
                    print_payload(addrMeta, payLoad)
                    print "\n\rRead IAS_CIE_Address - 0x0010 "
                    Destination = (address_64, 0x01, 0x0104, 0x0500)
                    payLoad, addrMeta = send_it(Destination, 0x01, "\x00"+"\xAA"+"\x00"+"\x10\x00", 100)
                    print_payload(addrMeta, payLoad)

                    #  Send Zone Enrol Response
                    temp = 0xff
                    node_info_dict[i]["ZoneNumber"] = temp
                    send_enrol_response(address_64, temp) #  NO REPLY EXPECTED
                    #  sleep(1)

                    # Get Zone Device State
                    print "State!"
                    payLoad, addrMeta = get_zone_state_attribute(address_64, auto_transaction_number(), 5)  #
                    print_payload(addrMeta, payLoad)


# Simple Descriptor Request. Returns Device descriptors.
def simple_descriptor_request(address_64, sAddress): # Simple Descriptor Request
    address_check = construct_address(address_64)
    print "\n\rSimple Descriptor Request - 0x0004 - Sensor : ", address_64
    #                                 HA /ZDO|Cluster ID
    Destination = (address_64, 0x00, 0x0000, 0x0004)
    payload1, addressStuff = send_it(Destination, 0x00, chr(auto_transaction_number()) + sAddress + chr(0x01), 100, 5)
    return payload1, addressStuff


# Routing table request. Yeah works but you shouldn't need it!
def routing_table_request(router_address_64, trans_number, startIndex):
    address_check = construct_address(router_address_64)
    #                       | Application Profile | Cluster ID
    Destination = (router_address_64, 0x00, 0x0000, 0x0032 )
    payload, addrMeta = send_it(Destination, 0x00, chr(auto_transaction_number()) + chr(startIndex), 100)
    print addrMeta

    print_payload(addrMeta, payload)

# Because the routers we purchased are crap and retain their routing table we must filter out
# no responsive nodes. As this is the first transmission this is the best place to do this.
# get basic node data.
def get_basic_node_data2(ias_node_dictionary):
    #  Get Basic data from all end nodes in the node list and create a node dictionary with
    #  this information, and delete non responsive nodes ie those still in the routing table.
    the_ias_dict = {}

    counter = 0
    ias_position_counter = 0
    altered = False

    for i in range(len(ias_node_dictionary)):
        address_64, address_16 = get_addresses(ias_node_dictionary, i)
        address_16_string = get_16_bit_address_string(ias_node_dictionary, i)
        buffer = address_64.strip('!')
        address_check = "[" + buffer + "]!"
        loop_counter = 0
        while True:
            payLoad, addrMeta = simple_descriptor_request(address_64, address_16)
            print address_check
            print addrMeta, payLoad
            # Payload received from IAS device.
            if payLoad != False and address_check == addrMeta[0]:
                if ord(payLoad[1]) == Message_Success and addrMeta[3] == Simple_Desc_Response:
                    simpleDescResponse = SimpleDescriptorResponse()  # Instantiate data type Instance; Simple Descriptor Response class.
                    #  Return Dictionary
                    the_ias_dict[ias_position_counter] = simpleDescResponse.setData(payLoad, address_64, address_16_string)
                    ias_position_counter += 1
                    del simpleDescResponse
                    break
            # TIME OUT! Must be a environment sensor / OR ROUTER!!! or unfortunately a device that was just on the network but now removed, crap.
            elif loop_counter >= 3:
                print "deleting non responsive node: ", ias_node_dictionary[i], " from immediate live node list "
                del ias_node_dictionary[i]
                node_temp_dict = {}

                counter = 0
                for j in ias_node_dictionary.keys():
                    node_temp_dict[counter] = {}
                    node_temp_dict[counter] = ias_node_dictionary[j]  # Each entry
                    counter += 1
                altered = True
                break
            else:
                loop_counter +=1
    if altered:
        return the_ias_dict, node_temp_dict
    else:
        return the_ias_dict, ias_node_dictionary


# Returns basic end node data. Uses 'Device' data type see zigsClass.py
# Places end devices into IAS node dictionary.
def get_basic_node_data(ias_node_dictionary):
    #  Get Basic data from all end nodes in the node list and create a node dictionary with
    #  this information
    the_ias_dict = {}
    environment_node_dictionary = {}
    counter = 0
    ias_position_counter = 0
    altered = False

    for i in range(len(ias_node_dictionary)):
        address_64, address_16 = get_addresses(ias_node_dictionary, i)
        address_16_string = get_16_bit_address_string(ias_node_dictionary, i)

        while True:
            payLoad, addrMeta = simple_descriptor_request(address_64, address_16)
            print addrMeta, payLoad
            # Payload received from IAS device.
            if payLoad != False:
                if ord(payLoad[1]) == Message_Success and addrMeta[3] == 0x8004:
                    simpleDescResponse = SimpleDescriptorResponse()  # Instantiate data type Instance; Simple Descriptor Response class.
                    #  Return Dictionary
                    the_ias_dict[ias_position_counter] = simpleDescResponse.setData(payLoad, address_64, address_16_string)
                    ias_position_counter += 1
                    del simpleDescResponse
                    break
            # TIME OUT! Must be a environment sensor / OR ROUTER!!! or unfortunately a device that was just on the network but now removed, crap.
            else:
                print "deleting non responsive node: ", ias_node_dictionary[i], " from immediate live node list "
                del ias_node_dictionary[i]
                node_temp_dict = {}

                counter = 0
                for j in ias_node_dictionary.keys():
                    node_temp_dict[counter] = {}
                    node_temp_dict[counter] = ias_node_dictionary[j]  # Each entry
                    counter += 1
                altered = True
                break

    '''
    simpleDescResponse = SimpleDescriptorResponse()
    environment_node_dictionary[counter] = ias_node_dictionary[i]  # Record the environment sensor to a separate list/Dict
    the_ias_dict[ias_position_counter]  = simpleDescResponse.setDataEnviro()
    ias_position_counter = ias_position_counter + 1
    del simpleDescResponse
    '''

    if altered:
        return the_ias_dict, environment_node_dictionary, node_temp_dict
    else:
        return the_ias_dict, environment_node_dictionary, ias_node_dictionary


# Auto incrementing Transaction Number. Just for Dev.
def auto_transaction_number():
    global TRANS_NUMBER
    TRANS_NUMBER += 0x01
    if TRANS_NUMBER >= 0xFF:
        TRANS_NUMBER = 0x00
    return TRANS_NUMBER

# Auto incrementing Zone Number. Just for Dev.
def auto_zone_number():
    global ZONE_NUMBER
    ZONE_NUMBER += 0x01
    if ZONE_NUMBER >= 0xFF:
        ZONE_NUMBER = 0x00
    return ZONE_NUMBER


# Convert 64Bit address to Little Endian
def convert_address_to_little_endian(address_64):
    # Make 64Bit address
    # Strip out '[', ']', and '!'
    str1 = address_64
    str2 = str1.strip('!][')
    newString = ""
    for x in reversed(range(0, len(str2))):  # Reverse the BYTE order
        if str2[x] != ':':
            newString += str2[x]
            x += 1

    anotherString = ""
    for x in range(0, len(newString), 2):
        anotherString += newString[x+1]
        anotherString += newString[x]

    LEaddress = binascii.unhexlify(anotherString)

    return LEaddress

# Get Time Stamp
# YOU MUST SET THE TIME ZONE ON THE DEVICE FROM THE DEVICE MANAGEMENT WEB PAGE!
# Returns current time in ISO format as per the time settings (timezone) on the device
def get_time_stamp():
    # Print the Current Local time.
    eight_hours_from_now = datetime.now().isoformat()
    current_time = eight_hours_from_now
    return current_time


# Table Node List. Prints Node List in a table (Node List is a Dict)
# Returns Coordinator Address.
def table_node_list(node_list):
        # Print the table:
    print "%12s %12s %8s %24s" % ("Label", "Type", "Short", "Extended")
    print "%12s %12s %8s %24s" % ("-" * 12, "-" * 12, "-" * 8, "-" * 24)
    for node in node_list:
        print "%12s %12s %8s %12s" % (node.label, node.type, node.addr_short, node.addr_extended)


# Filters node list and returns coordinator address.
def get_coordinator_address(node_list):
    for node in node_list:
        if node.type == "coordinator":
            str1 = node.addr_extended
    buffer = str1.strip('!]:[')
    coordinatorAddress = convert_address_to_little_endian(buffer)
    return coordinatorAddress


# Filters node list and returns coordinator address.
def get_router_address(node_list):
    success = False
    router_list = []
    for node in node_list:
        if node.type == "router":
            router_list.append(node.addr_extended)

    return router_list

# Creates a Dictionary of Nodes
# Ignores Coordinator
# Removes routers and coordinators
def create_node_dictionary(node_list, enviroDict):

    environment_device_list = []

    for x in enviroDict.keys():
        if enviroDict[x]['long_address'] not in environment_device_list:
            environment_device_list.append(enviroDict[x]['long_address'])


    # We use filter to remove any coordinators from our list
    # We use filter to remove any routers from our list
    # We use filter to remove any Environment Sensors from our list
    node_list = filter(lambda x: x.type != 'coordinator', node_list)
    node_list = filter(lambda x: x.type != 'router', node_list)
    node_list = filter(lambda x: x.addr_extended not in environment_device_list, node_list)

    # We use map to get the extended and short address of each node
    node_type_list = map(lambda x: x.type, node_list)
    node_64Bit_address_list = map(lambda x: x.addr_extended, node_list)
    node_16Bit_address_list = map(lambda x: x.addr_short, node_list)

    # We create a nested dictionary to hold our sample data
    res = {i: (node_64Bit_address_list[i], node_type_list[i], node_16Bit_address_list[i]) for i in range(len(node_list))}
    return res

def create_router_dictionary(node_list):

    # We use filter to remove any coordinators from our list
    # We use filter to remove any Environment Sensors from our list
    node_list = filter(lambda x: x.type != 'coordinator', node_list)
    node_list = filter(lambda x: x.type != 'end', node_list)

    # We use map to get the extended and short address of each node
    node_type_list = map(lambda x: x.type, node_list)
    node_64Bit_address_list = map(lambda x: x.addr_extended, node_list)
    node_16Bit_address_list = map(lambda x: x.addr_short, node_list)

    # We create a nested dictionary to hold our sample data
    res = {i: (node_64Bit_address_list[i], node_type_list[i], node_16Bit_address_list[i]) for i in range(len(node_list))}
    return res


# Create Device friendly addresses 64bit(little endian) and 16bit
def get_addresses(endDeviceList, deviceNumber):

    # Make 64Bit address
    # Strip out [,] and !
    str1 = endDeviceList[deviceNumber][0]
    str2 = str1.strip('!][')
    address_64 = ("%s%s" % (str2, "!"))  # put back "!"

    # Make 16Bit address Little Endian.
    # Strip out [,] and !
    str1 = endDeviceList[deviceNumber][2]
    str2 = str1.strip('!][')
    buffer = (str2[2] + str2[3] + str2[0] + str2[1])  # Create 16Bit_Address Little+ Endian
    address_16 = binascii.unhexlify(buffer)
    print buffer
    return address_64, address_16

# Create Device friendly addresses 64bit(little endian) and 16bit
def get_address64(endDeviceList, deviceNumber):

    # Make 64Bit address
    # Strip out [,] and !
    str1 = endDeviceList[str(deviceNumber)]['address']
    str2 = str1.strip('!][')
    address_64 = ("%s%s" % (str2, "!"))  # put back "!"
    return address_64


def get_16_bit_address_string(endDeviceList, deviceNumber):
    # Make 64Bit address
    # Strip out [,] and !
    str1 = endDeviceList[deviceNumber][2]
    #str2 = str1.strip('!][')
    #address_16 = ("%s%s" % (str2, "!"))  # put back "!"
    return str1


# Send, No reply.
# Sends message and doesn't expect a reply payload; needed in IAS Zone Enrollment.
def send_no_reply(destination, DestEndpoint, message, cluster):

    sd = socket(AF_ZIGBEE, SOCK_DGRAM, XBS_PROT_TRANSPORT)
    sd.bind(("", DestEndpoint, 0, 0))
    print "Sending"
    sd.sendto(message, 0, destination)


# Sends and Receives Data.
# ToDo : Could be improved?
def send_it(destination, DestEndpoint, message, bufferLength, timeout = 20):

    sd = socket(AF_ZIGBEE, SOCK_DGRAM, XBS_PROT_TRANSPORT)
    sd.bind(("", DestEndpoint, 0, 0))
    print "Sending"
    sd.sendto(message, 0, destination)
    #for x in range(x):
    try:
        sd.settimeout(timeout)
        payload, addrMeta = sd.recvfrom(bufferLength)
        print "Received"
        return payload, addrMeta
    except:
        print "timeout"

    print "Received"
    return False, False

def send_to_switch(address64, command):
    # Destination Tuple                | Application Profile | Cluster ID
    Destination = (address64, 0x01, Home_Automation_Cluster_ID, On_Off_Cluster)
    #                 sendit(|Destination tuple, Cluster Command, |Frame Control|Trans Sequence number|Off/On/Toggle|, message timeout time)
    payLoad, addrMeta = send_it(Destination, Write_Attributes, Cluster_Specific + chr(auto_transaction_number()) + chr(command), 100)
    print_payload(addrMeta, payLoad)


# Dev only; NOT USED!
def sendIt_N_hang(destination, DestEndpoint, message, bufferLength, cluster):
    if cluster == 0x0001:  # Cluster 0x0001 response 0x8001 gets sent 2 times from the end device.
        x = 2  # 2             #So we have to clear the buffer twice. May only be Motion sensor.
    else:  # Yes Only Motion sensor
        x = 1
    sd = socket(AF_ZIGBEE, SOCK_DGRAM, XBS_PROT_TRANSPORT)
    sd.bind(("", DestEndpoint, 0, 0))
    print "Sending"
    sd.sendto(message, 0, destination)
    for x in range(x):
        payload, src_addr = sd.recvfrom(bufferLength)
    print "Received"
    print "src_addr: ", src_addr
    print "len(payload): %d" % len(payload)
    if ord(payload[1]) == 0:
        print "SUCCESS!"
    for index, byte in enumerate(payload):
        print "payload[%d] = %s (%d)" % (index, hex(ord(byte)), ord(byte))
    # sd.close()
    sleep(2)


# prints the payload and address meta data.
def print_payload(addrDetail, Payload):
    print "src_addr: ", addrDetail
    print "len(payload): %d" % len(Payload)
    if ord(Payload[1]) == 0:
        print "SUCCESS!"
    for index, byte in enumerate(Payload):
        print "payload[%d] = %s (%d)" % (index, hex(ord(byte)), ord(byte))

