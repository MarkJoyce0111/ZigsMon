# GeriMon ZigBee Gateway Code.
# By Mark Joyce 2020.
# Computer Science Dept .
# Edith Cowan University.

# For the School of Nursing and Midwifery; @ECU.
# Project Leads Dr Dana Dermody and Dr Naeem Janjua.

# TODO add friendly name to temp / humid sensor payload.
import sys, os
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

def getInput(displayString, decisions, errorString):
    while(1):
        print displayString
        userIn = raw_input()

        for check in(range(len(decisions))):
            if userIn.lower() == decisions[check]:
                return decisions[check]

        print errorString
        sleep(4)
        os.system('clear')



def main():

    # Perform node discovery.
    Live_node_list = zigbee.getnodelist(refresh=True, discover_zigbee=True)

    # Display a node list table. Debug/Development.
    table_node_list(Live_node_list)

    print ""
    UserIn = getInput("Do you need to enroll any temperature/humidity sensor/s", ["y", "n"], "Input Error, please try again")
    if UserIn == "y":
        environment_node_dict = enrol_enviro_sensors()

        if environment_node_dict != None:
            environment_node_dict = check_info_file(environment_node_dict,'dictEnviro.json')

        dump_back_nodes = json.dumps(environment_node_dict, indent=4) # We convert the dictionary to JSON format

        # We write the JSON object to back to file so the new device can have its friendly_name changed.
        f = open('dictEnviro.json',"w")
        f.write(dump_back_nodes)
        f.close()
        print environment_node_dict

    else:
        f = open('dictEnviro.json', "r")
        data = f.read()
        f.close()
        environment_node_dict = json.loads(data)  # We convert the JSON object to a Dictionary


    # Get coordinators address. This Section, Not needed, for future development.
    coordinator_address = get_coordinator_address(Live_node_list)
    print coordinator_address # Debug
    router_address = get_router_address(Live_node_list)
    print router_address # Debug

    # Remove Coordinator from node list and create a dictionary of end nodes.
    raw_node_dictionary = create_node_dictionary(Live_node_list, environment_node_dict)
    print raw_node_dictionary # Debug
    # Check the node file, load friendly names, and add any new devices.
    file_node_list = check_file(raw_node_dictionary, 'dict.json')

    # Create an end node information dictionary
    # Get basic Node data. IAS node data and Lumi (Environment) node data.
    # Returns : Intruder Alarm System device info, Environmental Node device list/ Dict, Raw/ Live node dictionary.
    # raw_node_dictionary can have devices removed therefore it is returned however, it should be a pointer,
    # Todo investigate pointer.
    #ToDo Evironmental Node Dict is not implemeted, was removed when routers were introduced. UPDATE: Is Now!
    ias_node_info_dict, raw_node_dictionary = get_basic_node_data2(raw_node_dictionary)

    # Check for and enrol IAS devices.
    # We will be adding fields to the ias node info dict, so that is why it is ias_node_info_dict is returned
    #ias_node_info_dict = ias_device_enrol(raw_node_dictionary, ias_node_info_dict, coordinator_address)
    file_node_info = check_info_file(ias_node_info_dict, 'dictNodeInfo.json')

    ######################################################
    #  Debug.                                            #
    ######################################################
    print":::::::::::::::::::::::::::::::::::::::::::"
    print "Live Node List"
    print json.dumps(raw_node_dictionary, indent=4)
    print":::::::::::::::::::::::::::::::::::::::::::"
    print":::::::::::::::::::::::::::::::::::::::::::"
    print "File Node List"
    print json.dumps(file_node_list, indent=4)
    print":::::::::::::::::::::::::::::::::::::::::::"
    print":::::::::::::::::::::::::::::::::::::::::::"
    print "File Node Info"
    print json.dumps(file_node_info, indent=4)
    print":::::::::::::::::::::::::::::::::::::::::::"
    ######################################################

    setParams(file_node_list)
    print "File Node List"
    print json.dumps(file_node_list, indent=4)

    dump_back_nodes = json.dumps(file_node_list, indent=4) # We convert the dictionary to JSON format

    # We write the JSON object to back to file so the new device can have its friendly_name changed.
    f = open('dict.json',"w")
    f.write(dump_back_nodes)
    f.close()


    '''
    #  Identity Function Test Future Implementation.
    #  Tell all IAS devices to identify themselves. Eg Flash their inbuilt LEDs
    for i in range(len(raw_node_dictionary)):
        address_64 = get_addresses2(file_node_list, i)  # get the device addresses from the node dictionary
        identify_end_device(address_64, 10)  # Flash for 5 seconds
    sleep(5)
    #  Tell IAS devices to stop identifying themselves.
    for i in range(len(raw_node_dictionary)):
        address_64, address_16 = get_addresses(raw_node_dictionary, i)  # get the device addresses from the node dictionary
        end_identify_end_device(address_64)
    '''


    while 1:

        print "Do you want to enroll all the devices?; Required! -  \'Y\' or \'N\'"
        decision = raw_input()
        if decision.lower() == "y":
            ias_node_info_dict = ias_device_enrol(raw_node_dictionary, ias_node_info_dict, coordinator_address)
            dump_back_nodes = json.dumps(ias_node_info_dict, indent=4) # We convert the dictionary to JSON format
            # We write the JSON object to back to file so the new device can have its friendly_name changed.
            f = open('dictNodeInfo.json',"w")
            f.write(dump_back_nodes)
            f.close()
            break

        elif decision.lower() == "n":
            break

        else:
            print "\nPlease try again!\n"
            sleep(4)
            os.system('clear')
        # Enter message receive loop.

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



    print "\n", "*" * 25, " All Done! ", "*" * 25 ,"\n"
    #receive_Loop2(f_n_info_dict, e_info_dict, f_node_dict)



def setParams(file_node_dictionary):
    print "Set all the devices out in-front of you with the LED side facing up"
    print "One by one the LED on each device will be set to flash.\n Please select an appropriate friendly name for the device"
    print "Press enter to continue"

    raw_input()
    os.system('clear')
    for x in file_node_dictionary.keys():
        print "\n"
        print "Device Address: ", file_node_dictionary[x]['address']
        print "Friendly Name: ", file_node_dictionary[x]['friendly_name']
        address_64 = get_address64(file_node_dictionary, x)  # get the device addresses from the node dictionary
        identify_end_device(address_64, 20)  # Flash for 5 seconds
        print "Please Enter a friendly name"
        decision = raw_input()
        file_node_dictionary[x]['friendly_name'] = decision
        end_identify_end_device(address_64)

        print "Done\n"


def enrol_enviro_sensors():
    sd = socket(AF_ZIGBEE, SOCK_DGRAM, XBS_PROT_TRANSPORT)
    sd.bind(("", 1, 0, 0))
    enviro_list = []
    friendly_name_list = []
    res = {}
    print "Press button on the environment sensor 3 times simultaneously, then blow into the sensor grill"
    while True:
        #print "Press button on sensor 3 times simultaneously"
        payload, src_addr = sd.recvfrom(100) #ToDo
        print "*" * 20, "Received", "*" * 20
        address = src_addr[0]
        #print "From Address: ", address
        #print "From Address Data: ", src_addr
        print "Address String = ", src_addr[0]
        print "Endpoint = ", src_addr[1]
        print "Profile ID = ", Profile_Type[src_addr[2]]
        print "Cluster ID = ", Member_Cluster[src_addr[3]]

        #print_payload(src_addr, payload)
        if src_addr[2] == Home_Automation_Cluster_ID and src_addr[3] == Relative_Humidity_Measurement or src_addr[3] == Temperature_Measurement:
            print "Found a Device!"
            if address not in enviro_list:
                print "Adding : ", address, " to list."
                enviro_list.append(address)
                print "enviro_list is : ", enviro_list
                print "Give it a friendly name"
                decision = raw_input()
                friendly_name_list.append(decision)
                print " Do you want to add another device? \'Y\' for yes and \'N\' for no"
                decision = raw_input()
                if decision.lower() == "y":
                    pass
                elif decision.lower() == "n":

                    res = {i: {'long_address': enviro_list[i], 'friendly name': friendly_name_list[i]} for i in range(len(enviro_list))}
                    print res
                    return res

                else:
                    print "Please try again"

            elif address in enviro_list:
                while 1:

                    print "Device: ", address, "is already in list"
                    print " Do you want to add another device? \'Y\' for yes and \'N\' for no"
                    decision = ""
                    decision = raw_input()
                    if decision.lower() == "y":
                        break
                    elif decision.lower() == "n":
                        res = {i: {'long_address': enviro_list[i], 'friendly name': enviro_list[i]} for i in range(len(enviro_list))}
                        print res
                        return res

                    else:
                        print "\nPlease try again!\n"




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

        # ToDo make this section work for all relative humidity and temperature measurements.
        # ToDo OR make some kind of commissioning system, ie push button, OR menu based. DONE!!!!
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

    # sd.close()




main()
