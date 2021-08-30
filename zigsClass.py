#Class for reply messages. Device Class not used.
class SimpleDescriptorResponse:
    instances = []
    entryNumber = 0
    def __init__(self):

        self.instances.append(self)
        self.__status = 0x01  # failure
        self.__long_address = ""
        self.__short_network_address = ""
        self.__descriptor_length = 0x00
        self.__node_endpoint = 0x00
        self.__application_profile_id = 0x0000
        self.__application_device_version = 0x00
        self.__input_cluster_count = 0x00
        self.__input_cluster_list = []
        self.__output_cluster_count = 0x00
        self.__output_cluster_list = []
        self.__ias_device = False
        self.__temperature_measurement = False
        self.__enrolled = False
        self.__temp = 0

    def setDataEnviro(self):  # This is a walk around for the NON STANDARD sensors set the capabilities of the sensor
        self.__status = 0x00
        self.__short_network_address = 0x00
        self.__descriptor_length = 0x00
        self.__node_endpoint = 0x00
        self.__application_profile_id = 0x8002
        self.__input_cluster_count = 0x02
        self.__input_cluster_list = [0x0402, 0x0405]
        info_dictionary = {
                'short_address': self.__short_network_address,
                'status': self.__status,
                'descriptor_length': self.__descriptor_length,
                'node_endpoint': self.__node_endpoint,
                'application_profile_id': self.__application_profile_id,
                'input_cluster_count': self.__input_cluster_count,
                'input_cluster_list': self.__input_cluster_list,
                'ias_device': self.__ias_device,
                'temperature_measurement': True,
                'enrolled': self.__enrolled
            }

        return info_dictionary


    def setData(self, dataIn, Long_address, Short_address):  # Used to set the data of a STANDARD zigbee sensor.
        self.__status = ord(dataIn[1])
        print "status =", self.__status
        if(self.__status == 0): # If SUCCESS 0x00, extract the data
            #self.__short_network_address = ord(dataIn[3]) << 8 | ord(dataIn[2])
            self.__descriptor_length = ord(dataIn[4])
            self.__node_endpoint = ord(dataIn[5])
            self.__application_profile_id = ord(dataIn[7]) << 8 | ord(dataIn[6])
            self.__application_device_version = ord(dataIn[9]) << 8 | ord(dataIn[8])
            self.__application_device_version = ord(dataIn[10])
            self.__input_cluster_count = ord(dataIn[11])
            print "Input Cluster Count", self.__input_cluster_count
            for x in range(12, (self.__input_cluster_count * 2) + 12, 2):
                #print hex(ord(dataIn[x + 1]) << 8 | ord(dataIn[x]))
                self.__input_cluster_list.append(hex(ord(dataIn[x + 1]) << 8 | ord(dataIn[x])))
            print self.__input_cluster_list
            outputClusterIndex = (self.__input_cluster_count * 2) + 12
            self.__output_cluster_count = ord(dataIn[outputClusterIndex])
            print "Output cluster count", self.__output_cluster_count
            for x in range(outputClusterIndex + 1, (self.__output_cluster_count *2) + outputClusterIndex + 1, 2):
                #print hex(ord(dataIn[x + 1]) << 8 | ord(dataIn[x]))
                self.__output_cluster_list.append(hex(ord(dataIn[x + 1]) << 8 | ord(dataIn[x])))
            print self.__output_cluster_list
        #__temp = str(self.entryNumber)
        #  Create Dictionary of Node Data
        info_dictionary = {
            'long_address': Long_address,
            'short_address': Short_address,
            'status': self.__status,
            'descriptor_length': self.__descriptor_length,
            'node_endpoint': self.__node_endpoint,
            'application_profile_id': self.__application_profile_id,
            'application_device_version': self.__application_device_version,
            'input_cluster_count': self.__input_cluster_count,
            'input_cluster_list': self.__input_cluster_list,
            'output_cluster_count': self.__output_cluster_count,
            'output_cluster_list': self.__output_cluster_list,
            'ias_device': self.__ias_device,
            'temperature_measurement': self.__temperature_measurement,
            'enrolled': self.__enrolled
        }

        SimpleDescriptorResponse.entryNumber += 1
        return info_dictionary


# Device Class.
class Device:
    def __init__(self):

        self.__extendedAddress = "00:00:00:00:00:00:FF:FF!"  # 64 Bit Address
        self.__shortAddress = "\xFF\xFF"# 16 Bit Address
        self.__iasZoneDevice = False
        self.__zoneNumber = 0xFF
        self.__deviceType = 0x0000
        self.__iasZoneEndPointNumber = 0x00

    def setExtendedAddress(self, lAddr):
        self.__extendedAddress = lAddr

    def setShortAddress(self, sAddr):
        self.__shortAddress = sAddr

    def setIASdevice(self):
        self.__iasZoneDevice = True

    def setZoneNumber(self, zone_number):
        self.__zoneNumber = zone_number

    def setDeviceType(self, device_type):
        self.__deviceType = device_type

    def setIASendpointNumber(self, endpoint_number):
        self.__iasZoneEndPointNumber = endpoint_number

    def getExtendAddress(self):
        return self.__extendedAddress

    def getShortAddress(self):
        return self.__shortAddress

    def isIASDevice(self):
        return self.__iasZoneDevice

    def getDeviceType(self):
        return self.__deviceType

    def getIASEndPoint(self):
        return self.__iasZoneEndPointNumber

