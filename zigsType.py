# ZigBee Data Types
EUI64 = "\xF0"
# Time Zone Vars
Perth_TimeZone = 8
############################################
# ZDO (ZigBee Device Object) Commands      #
# Command                 Cluster ID       #
############################################

Network_Address_Request = 0x0000
IEEE_Address_Request = 0x0001
Node_Descriptor_Request = 0x0002
Simple_Descriptor_Request = 0x0004
Active_Endpoints_Request = 0x0005
Match_Descriptor_Request = 0x0006
Mgmt_LQI_Request = 0x0031
Mgmt_Routing_Request = 0x0032
Mgmt_Leave_Request = 0x0034
Mgmt_Permit_Joining_Request = 0x0036
Mgmt_Network_Update_Request = 0x0038

############################################
# ZCL (ZigBee Cluster Library) Clusters    #
# Clusters                                 #
############################################

# Basic Cluster ID
Basic_Cluster_ID = 0x0000
Power_Config_Cluster = 0x0001
Device_Temp_Config_Cluster = 0x0002
Identify_Cluster = 0x0003
Groups_Cluster = 0x0004
Scenes_Cluster = 0x0005
On_Off_Cluster = 0x0006
On_Off_Switch_Config_Cluster = 0x0007
Level_Control_Cluster = 0x0008
Alarms_Cluster = 0x0009
Binary_Input_Cluster = 0x000F

# On/Off/Toggle
OFF = 0x00
ON = 0x01
TOGGLE = 0x002

# Basic Cluster Attributes (Attribute ID)
Application_Version = 0x0001
Hardware_Version = 0x0003
Model_Identifier = 0x0005
############################################

# Attributes / Attribute ID
Identify_Time = 0x0000
############################################
# Time_Cluster
Time_ = 0x000A
# Attribute
Time__ = 0x0000
Time_Status = 0x0001
Time_Zone = 0x0002
############################################

# ZCL (ZigBee Cluster Library) Command Frames
# Cluster Commands - Command ID [ZCL chapter 2 page 8]
###########################################
Read_Attributes = 0x00  # Read Attributes
Read_Attributes_Response = 0x01
Write_Attributes = 0x02
Write_Attributes_Undivided = 0x03  # Write Attributes Undivided
Write_attributes_Response = 0x04
Write_Attributes_No_Response = 0x05  # Write Attributes No Response
Configure_Reporting = 0x06  # Configure Reporting
Configure_Reporting_Response = 0x07  # Configure Reporting Response
Read_Reporting_Configuration = 0x08  # Read Reporting Configuration
Read_Reporting_Configuration_Response = 0x09  # Read Reporting Configuration Response
Report_Attributes = 0x0A  # Report Attributes
Default_Response = 0x0b  # Default Response
Discover_Attributes = 0x0C
Discover_Attributes_Response = 0x0D


###########################################

# ZCL Frame Control Field
###########################################
Entire_Profile = "\x00"
Cluster_Specific = "\x01"
###########################################

#####################################################
# ZigBee HOME AUTOMATION PUBLIC APPLICATION PROFILE #
#####################################################
Home_Automation_Cluster_ID = 0x0104

Relative_Humidity_Measurement = 0x0405  # Relative Humidity
Temperature_Measurement = 0x0402  # Temperature Measurement

# ZCL (ZigBee Cluster Library) Commands
# Cluster Commands - Command ID
###########################################
NWK_addr_req = 0x0000
IEEE_addr_req = 0x0001
Node_Desc_req = 0x0002
Power_Desc_req = 0x0003
Simple_Desc_req = 0x0004
Active_EP_req = 0x0005
Match_Desc_req = 0x0006
Complex_Desc_req = 0x0010
Extended_Simple_Desc_req = 0x001D
Extended_Active_EP_req = 0x001E
Bind_req = 0x0021
Unbind_req = 0x0022

# more
# ZCL Command Attributes
###########################################
IAS_Zone = 0x0500
# IAS Zone Commands
Zone_State = "\x00\x00"
Zone_Type = 0x0001
Zone_Status = 0x0002
# Zone Settings Attribute Set
###########################################
IAS_CIE_Address = "\x10\x00"
ZoneID = "\x11\x00"
Zone_Enroll_Response = "\x00"
# Enroll Response Code
###########################################
Enroll_Success = "\x00"
Enroll_Not_Supported = "\x01"
Enroll_No_Enroll_Permit = "\x02"
Enroll_Too_Many_Zones = "\x03"
# Intruder Alarm System Zone (IAS Zone) Cluster ID's

# Simple Descriptor Response (0x8004) Variable
Simple_Desc_Response = 0x8004

Message_Success = 0x00

# End device types
Device_Type = {
    0x0d: 'Motion sensor',
    0x15: 'Contact switch'}

#Device profiles
Profile_Type = {
    0x0000: 'ZDO - ZigBee Device Object',
    0x0104: 'HA - Home Automation'}

# Member clusters
Member_Cluster = {
    0x0000: 'Basic Cluster',                # General
    0x0001: 'Power Configuration Cluster',
    0x0003: 'Identify Cluster',
    0x0004: 'Groups Cluster',
    0x0006: 'On/Off',
    0x0007: 'On/Off Switch Configuration',
    0x0008: 'Level Control',
    0x0009: 'Alarms',
    0x000A: 'Time Cluster',
    0x000C: 'Analogue Input',
    0x000D: 'Analogue Output',
    0x000F: 'Binary Input ',
    0x0010: 'Binary Output',
    0x0012: 'Multi-state Input',
    0x0013: 'Multi-state Output',
    0x0020: 'Poll Control',
    0x001A: 'Power Profile',
    0x0B05: 'Diagnostics',
    0x0400: 'Luminance Measurement',      # Measurement and Sensing
    0x0401: 'Luminance Level Sensing',
    0x0402: 'Temperature Measurement',
    0x0403: 'Pressure Measurement',
    0x0404: 'Flow Measurement',
    0x0405: 'Relative Humidity Measurement',
    0x0406: 'Occupancy Sensing',
    0x0B04: 'Electrical Measurement',
    0x0500: 'IAS Zone Cluster'}
