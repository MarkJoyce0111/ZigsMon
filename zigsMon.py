#Mark Joyce 2020
import zigbee
from zigbee import *
from zigsFunctz import *

# Import My modules
sys.path.append("importlibs.zip")

import urllib3

urllib3.disable_warnings()
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs='/etc/ssl/certs/ca-certificates.crt')

#  Globals. Not really needed.
TRANS_NUMBER = 0 #Dev Variable. A assignable number to each packet.
ZONE_NUMBER = 0 #Dev Variable. A assignable number to each end device.
rec_timeout = 20 # Message Time Out.

#  HTTPS
headers = {'content-type': 'application/json'}
url = 'https://gerimonapi.azurewebsites.net/api/geridatas'

######################################################
##  Get the temperature from motion and door sensor ##
##  Caution! May miss other incomming sensor data.  ##
##  It rejects messages from other devices whilst   ##
##  waiting for device temp message.                ##
                                                    ##
GET_IAS_TEMP = False                                ##
######################################################


def main():

    # Perform node discovery.
    Live_node_list = zigbee.getnodelist(refresh=True, discover_zigbee=True)

    # Display a node list table. Debug/Development.
    table_node_list(Live_node_list)

    # Load White List Data.
    f = open('dictNodeInfo.json', "r")
    data = f.read()
    f.close()
    f_n_info_dict = json.loads(data)  # We convert the JSON object to a Dictionary

    f = open('dictEnviro.json', "r")
    data = f.read()
    f.close()
    e_info_dict = json.loads(data)  # We convert the JSON object to a Dictionary

    f = open('dict.json', "r")
    data = f.read()
    f.close()
    f_node_dict = json.loads(data)  # We convert the JSON object to a Dictionary

    # Receive Data.
    receive_Loop2(f_n_info_dict, e_info_dict, f_node_dict)



def receive_Loop2(file_node_info_dict, environment_info_dict, file_node_dict):

    sd = socket(AF_ZIGBEE, SOCK_DGRAM, XBS_PROT_TRANSPORT)
    sd.bind(("", 1, 0, 0))

    while True:
        inDict = False
        InWhiteList = False
        friendly_name = ""
        '''    revcfrom return data   http://cms.digi.com/resources/documentation/digidocs/90001537/#references/r_xbee_extensions_to_python_socket.htm%3FTocPath%3DWorking%2520with%2520Zigbee%7C_____26
        
                          [0]          [1]        [2]          [3]                [4]               [5]
        src_addr = {Address String, Endpoint, Profile ID, Source Cluster ID, options bit mask, transmission_id }
        '''
        payload, src_addr = sd.recvfrom(100) # WAITS HERE! for message. No timeout.
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

                # Node in the node dict check routers by comparing whitelist in file.
                #  Get the Node info.

                for x in range(len(file_node_dict)):
                    if file_node_dict[str(x)]['address'] == address:
                        # print node_dictionary[x][0], "is equal to", address
                        node_dict_data_out_long_address = file_node_dict[str(x)]['address']
                        #node_dict_data_out_short_add = None # file_node_list[x][2]
                        friendly_name = file_node_dict[str(x)]['friendly_name']
                        InWhiteList = True
                        for x in range(len(file_node_info_dict)):
                            if file_node_info_dict[str(x)]['long_address'] == compare_address:
                                node_info_dict_data_out = file_node_info_dict[str(x)]
                        break


                # Must be from a router!
                if InWhiteList == True:
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
                            "shortaddress": str(node_info_dict_data_out['short_address']),
                            "devicefriendlyname": friendly_name,
                            "devicetemperature": temperature,
                            "devicetype": Device_Type[node_info_dict_data_out ["device_type"]],
                            "devicestate": state_out,
                            "zoneid": zone_id,
                            "batterystate": battery_out }
                    else:
                        payload_out = {
                            "timestamp": get_time_stamp(),
                            "longaddress": str(node_dict_data_out_long_address),
                            "shortaddress": str(node_info_dict_data_out['short_address']),
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
                for x in file_node_dict.keys():
                        if file_node_dict[x]['address'] == node_dict_data_out_long_address:
                            friendly_name = file_node_dict[x]['friendly_name']
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

main()
