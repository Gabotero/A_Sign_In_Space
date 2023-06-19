import numpy as np
import matplotlib.pyplot as plt
from construct import *
import collections
import time

##############################################################################
COLOR_RED = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_BLUE = '\033[94m'
COLOR_RESET = '\033[0m'
##############################################################################

frame_size = 1115 # 8920/8 [bytes]
frames = np.fromfile('final_decoded_frames.u8', dtype = 'uint8')
frames = frames[:frames.size//frame_size*frame_size].reshape((-1, frame_size))
print('We have', frames.shape[0], 'frames')

# Check the CRC-16.

crc_table = [0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0]

def crc16_ccitt_false(data):
    crc = 0xffff
    for d in data:
        tbl_idx = ((crc >> 8) ^ d) & 0xff
        crc = (crc_table[tbl_idx] ^ (crc << 8)) & 0xffff
    return crc & 0xffff

crc_ok = np.array([crc16_ccitt_false(f) for f in frames]) == 0
print(np.sum(~crc_ok), 'frames have invalid CRC')

plt.figure(figsize = (15,15), facecolor = 'w')
plt.imshow(frames[crc_ok], interpolation = 'nearest', aspect = 0.4)
plt.show()

#-----------------------------------#
#- CCDS TM Space Data Link Packets -#
#-----------------------------------#

# Parse the TM/AOS Space Data Link primary headers. In this case, TM Space Data Link packets.
# The upper layer can be CCSDS Space Packets.
# Package "construct" can be used to define binary structures.
# Then it can encode or decode the defined structures for you.

TM_Primary_Header = BitStruct('transfer_frame_version_number' / BitsInteger(2), # Same field for both TM (0x00) and AOS (0x01).
                            'spacecraft_id' / BitsInteger(10),
                            'virtual_channel_id' / BitsInteger(3), 		# To separate different applications/kinds of data.
                            'ocf_flag' / Flag,
                            'master_channel_frame_count' / BitsInteger(8), 	# Used by the decoder to check for missing frames.
                            'virtual_channel_frame_count' / BitsInteger(8), 	# Each virtual channel has its own private counter.
                            'transfer_frame_secondary_header_flag' / Flag, 	# '1' if a secondary header is present.
                            'synch_flag' / Flag, 				# Signals the type of data present in Transfer Frame Data Field. '0' if octet-synchronized and forward-ordered Packets or Idle Data, '1' if VCA_SDU (Virtual Channel Access) inserted.
                            'packet_order' / Flag, 				# If the Synchronization Flag is set to ‘0’, the Packet Order Flag is reserved for future use by the CCSDS and is set to ‘0’. If the Synchronization Flag is set to ‘1’, the use of the Packet Order Flag is undefined. 
                            'segment_length_id' / BitsInteger(2), 		# Should be set to 'b'11' if synch_flag = 0. 
                            'first_header_pointer' / BitsInteger(11)) 		# Undefined if synch_flag = 1. If synch_flag = 0, position of the first octet of the first Packet that starts in the Transfer Frame Data Field.

# 1) The purpose of the First Header Pointer is to facilitate delimiting of variable-length
# Packets contained within the Transfer Frame Data Field by pointing directly to the
# location of the first Packet from which its length may be determined.

# 2) The locations of any subsequent Packets within the same Transfer Frame Data Field
# will be determined by calculating the locations using the length field of these Packets.

# 3) If the last Packet in the Transfer Frame Data Field of Transfer Frame N spills over into Frame
# M of the same Virtual Channel (N<M), the First Header Pointer in Frame M ignores the
# residue of the split Packet and indicates the start of the next Packet that starts in Frame M.

# If no packet starts in Transfer Frame Data Field, first_header_pointer = b'11111111111' (2047). Can happen because a packet extends accross more than one Transfer Frame.
# If the Transfer Frame contains only Idle Data in the Transfer Fram Data field, first_header_pointer = b'11111111110' (2046)


# Extract the TM Primary Headers and related information
primary_headers = [TM_Primary_Header.parse(bytes(f)) for f in frames[crc_ok]]
mcfc = np.array([p.master_channel_frame_count for p in primary_headers])
vcid = np.array([p.virtual_channel_id for p in primary_headers])
vcfc = np.array([p.virtual_channel_frame_count for p in primary_headers])
secondary_header_flags = np.array([p.transfer_frame_secondary_header_flag for p in primary_headers])
synch_flags = np.array([p.synch_flag for p in primary_headers])
segment_ids = np.array([p.first_header_pointer for p in primary_headers])

fhps = np.array([p.first_header_pointer for p in primary_headers])

for p in primary_headers[:5]:
    print(p)


count = collections.Counter(vcid)
for virt_channel, n in count.items():
	print(f"Virtual Channel ID {virt_channel}: {n} packets.")


#count = collections.Counter(fhps)
#for pointer, n in count.items():
#        print(f"First octet in {pointer}: {n} packets.")


print('Packets lost:', np.sum(np.diff(mcfc.astype('uint8')) - 1))

print("Number of secondary headers: ", sum([1 for value in secondary_header_flags if value]), " out of ", len(secondary_header_flags), "TM Space Data Link frames.")
print("Number of Synchronization Flags: ", sum([1 for value in synch_flags if value]), " out of ", len(secondary_header_flags), "TM Space Data Link frames.")
print("Segment_Length_IDs: ", segment_ids)



plt.plot(mcfc)
plt.title('Master channel frame counter')
plt.ylabel('MCFC value')
plt.xlabel('Frame number');
plt.show()


#-----------------------#
#- CCSDS Space Packets -#
#-----------------------#

# Space Packet Primary Header
SPP_Primary_Header = BitStruct('Packet_Version_Number' / BitsInteger(3),     # '000' for Space Packets.
                               'Packet_Type' / Flag, 			     # To distinguish Packets used for telemetry/reporting (b'0') from Packets used for telecommand/requesting (b'1').
                               'Secondary_Header_Flag' / Flag, 		     # Indicates the presence (b'1') or absence (b'0') of the Packet Secondary Header within this Space Packet.
                               'Application_Process_ID' / BitsInteger(11),   # APID shall provide the naming mechanism for the managed data path. (Similar to a port in TCP)
                               'Sequence_Flags' / BitsInteger(2),	     # May be used to indicate User Data. b'00' if the SPP contains a continuation segment of User Data, b'01' if the SPP contains the first segment of User Data, b'10' if the SPP contains the last segment of User Data, and b'11' if the SPP contains unsegmented User data.
			       'Packet_Seq_Count_or_Name' / BitsInteger(14), # Shall contain the Packet Sequence Count if telemetry packet (Packet_Type == b'0'), or either seq count or name if telecommand packet (Packet_Type == b'1').
			       'Packet_Data_Length' / BitsInteger(16))	     # Length count C that equals one fewer than the length (in octets) of the Packet Data Field.
									     # C = (Total Number of Octets in the Packet Data Field) – 1

print("--------------------------------------------------")
print("Starting the extraction of the Virtual Channels...")
print("--------------------------------------------------")

target_vcid = 0
fhp_idle = 2046
fhp_noStart = 2047
noStart_TM_frames = 0 # Frames with data but not containing the start of the packet.
idle_TM_frames = 0
normal_TM_frames = 0


first_pointer_found = False

SPP_stream_0 = np.array([], dtype = 'uint8')
last_data = (frame_size-1)-6

#for i in range(40):
for i in range(len(frames[crc_ok])):

	print("Frame #", i)
	current_vcid = primary_headers[i].virtual_channel_id
	print("\t - \033[3mvirtual_channel_id\033[0m: ", current_vcid)
	if current_vcid != target_vcid:
		print(COLOR_RED, "\t\033[1mNot the target Virtual Channel! Skipping frame...\033[0m", COLOR_RESET)
	else:
		fhp = primary_headers[i].first_header_pointer
		print("\t - \033[3mvirtual_channel_frame_count\033[0m: ", primary_headers[i].virtual_channel_frame_count)
		print("\t - \033[3mfirst_header_pointer\033[0m: ", fhp)

		if (fhp==fhp_idle):
			print(COLOR_BLUE, "\t\033[1mOnly Idle data inside! Skipping frame...\033[0m", COLOR_RESET)
			idle_TM_frames+=1 # We checked there are 0.
			break
		elif (fhp==fhp_noStart):
			print(COLOR_YELLOW, "\t\033[1mNo packet starts in Transfer Frame Data Field!\033[0m", COLOR_RESET)
			noStart_TM_frames+=1 # We checked there are 0, also.
			break
		else:

			print(COLOR_GREEN, "\t\033[1mExtracting data inside the frame...\033[0m", COLOR_RESET)
			normal_TM_frames+=1

			if (not first_pointer_found): # It is the first frame with a pointer to the first SPP packet.

				print("\t *** Found the first pointer to an SPP packet in the target Virtual Channel! ***")
				starts_at = TM_Primary_Header.sizeof() + fhp
				SPP_stream_0 = np.concatenate((SPP_stream_0, frames[i][starts_at:last_data+1]))
				first_pointer_found = True
			else:
				# Append frame data to the stream.
				SPP_stream_0 = np.concatenate((SPP_stream_0, frames[i][TM_Primary_Header.sizeof():last_data+1]))

	print("\n")

print("----------")
print("Summary:\n")
print("----------")
print('We have', frames.shape[0], 'frames')
for virt_channel, n in count.items():
	print(f"Virtual Channel ID {virt_channel}: {n} packets.")

print('Packets lost:', np.sum(np.diff(mcfc.astype('uint8')) - 1))
print(COLOR_YELLOW, "· Number of frames with no Starting packets: ", noStart_TM_frames, COLOR_RESET)
print(COLOR_BLUE, "· Number of Idle frames: ", idle_TM_frames, COLOR_RESET)
print(COLOR_GREEN, "· Number of Nominal frames: ", normal_TM_frames, COLOR_RESET)


plt.plot(mcfc)
plt.title('Master channel frame counter')
plt.ylabel('MCFC value')
plt.xlabel('Frame number');
plt.show()



first = True

version_numbers = []
packet_types = []
secondary_header_flags_SPP = []
apids = []
seq_flags = []
data_lengths = []

packets = 0
target_APID = 23
raw_target_APID_data = np.array([], dtype = 'uint8')
processed_target_APID_data = np.array([], dtype = 'uint8')

target_packets_lengths = []


PUS_Standard_Data_Field_Header = BitStruct('CCSDS_Secondary_Header_Flag_or_Spare' / Flag,
                               	    'TC_Packet_PUS_Version_Number' / BitsInteger(3),
                               	    'Spare_or_Ack' / BitsInteger(4),
                               	    'Service_Type' / BitsInteger(8),
                               	    'Service_Subtype' / BitsInteger(8))

PUS_Memory_Dump_6_6_Header = BitStruct('Unknown_Fields' / BitsInteger(8*8),
				       'Data_Length' / BitsInteger(8))

target_packets_PUS_types = []
target_packets_PUS_subtypes = []

SPP_Secondary_Header_length = 10 #(PUS_Standard_Data_Field_Header)

while (True):

	if(first):
		print("\t\t ** First SPP packet **")
		starts_at = 0
		first = False
	else:
		print("\t\t ** Getting next SPP packet **")
		starts_at = end_of_previous_SPP_packet

	SPP_Header = SPP_Primary_Header.parse(bytes(SPP_stream_0[starts_at:starts_at+SPP_Primary_Header.sizeof()])) # 0:6 (6 is exclusive)
	# End of this packet
	end_of_previous_SPP_packet = starts_at + SPP_Primary_Header.sizeof() + SPP_Header.Packet_Data_Length + 1

	print("end_of_previous_SPP_packet is ", end_of_previous_SPP_packet, " and length of stream is ", len(SPP_stream_0))

	if(SPP_Header.Application_Process_ID == target_APID):
		print(COLOR_GREEN, "\t\tFound SPP packet of target APID!", COLOR_RESET)
		if(SPP_Header.Secondary_Header_Flag):
			print(COLOR_YELLOW, "\t\tFound secondary header! Removing...", COLOR_RESET)
			data = SPP_stream_0[starts_at + SPP_Primary_Header.sizeof()+SPP_Secondary_Header_length:end_of_previous_SPP_packet] #(end_of_previous_SPP_packet excluded)

			head = PUS_Standard_Data_Field_Header.parse(bytes(SPP_stream_0[starts_at + SPP_Primary_Header.sizeof():end_of_previous_SPP_packet]))
			target_packets_PUS_types.append(head.Service_Type)
			target_packets_PUS_subtypes.append(head.Service_Subtype)
		else:
                        data = SPP_stream_0[starts_at + SPP_Primary_Header.sizeof():end_of_previous_SPP_packet]

		memory_dump_packet = PUS_Memory_Dump_6_6_Header.parse(data)
		raw_target_APID_data = np.concatenate((raw_target_APID_data, data[PUS_Memory_Dump_6_6_Header.sizeof():PUS_Memory_Dump_6_6_Header.sizeof()+memory_dump_packet.Data_Length]))

		target_packets_lengths.append(len(data))

	if((len(SPP_stream_0)-1) - end_of_previous_SPP_packet < SPP_Primary_Header.sizeof()):
		print(COLOR_BLUE, "\t\tCannot read more SPP Headers!", COLOR_RESET)
		break

	packets += 1
	# Print info and store statistics
	print("\t - \033[3mPacket_Version_Number\033[0m: ", SPP_Header.Packet_Version_Number)
	print("\t - \033[3mPacket_Type\033[0m: ", SPP_Header.Packet_Type)
	print("\t - \033[3mSecondary_Header_Flag\033[0m: ", SPP_Header.Secondary_Header_Flag)
	print("\t - \033[3mAPID\033[0m: ", SPP_Header.Application_Process_ID)
	print("\t - \033[3mSequence_Flags\033[0m: ", SPP_Header.Sequence_Flags)
	print("\t - \033[3mPacket_Seq_Count_or_Name\033[0m: ", SPP_Header.Packet_Seq_Count_or_Name)
	print("\t - \033[3mPacket_Data_Length\033[0m: ", SPP_Header.Packet_Data_Length + 1)
	version_numbers.append(SPP_Header.Packet_Version_Number)
	packet_types.append(SPP_Header.Packet_Type)
	secondary_header_flags_SPP.append(SPP_Header.Secondary_Header_Flag)
	apids.append(SPP_Header.Application_Process_ID)
	seq_flags.append(SPP_Header.Sequence_Flags)
	data_lengths.append(SPP_Header.Packet_Data_Length + 1)


print("Finished extracting SPP packets. Extracted: " , packets, " packets.\n")
count = collections.Counter(version_numbers)
for VN, n in count.items():
        print(f"- Version number #{VN}: {n} SPP packets.")

count = collections.Counter(packet_types)
for type, n in count.items(): # All of them are '0' (telemetry/reporting) and not requests.
        print(f"- Packet type {type}: {n} SPP packets.")


count = collections.Counter(secondary_header_flags_SPP)
for flag, n in count.items():
        print(f"- Secondary header flag {flag}: {n} SPP packets.")

print("--------------------------------------------------------------")

count = collections.Counter(apids) # APID = 2047 if idle packet.
for a, n in count.items():
        print(f"APID #{a}: {n} SPP packets.")

print("--------------------------------------------------------------")
count = collections.Counter(seq_flags)
for sf, n in count.items():
	if(sf == 0):
        	print(f"- Sequence flag #{sf} (Continuation of User Data): {n} SPP packets.")
	elif(sf == 1):
		print(f"- Sequence flag #{sf} (First segment of User Data): {n} SPP packets.")
	elif(sf == 2):
		print(f"- Sequence flag #{sf} (Last segment of User Data): {n} SPP packets.")
	else:
		print(f"- Sequence flag #{sf} (Unsegmented User Data): {n} SPP packets.")
print("-")

count = collections.Counter(target_packets_lengths)
for l, n in count.items():
        print(f"Packet Length #{l}: {n} APID {target_APID} packets. (After removing PUS_Standard_Data_Field_Header)")

print("-")

count = collections.Counter(target_packets_PUS_types)
for t, n in count.items():
        print(f"Type #{t}: {n} PUS packets.")

print ("-")

count = collections.Counter(target_packets_PUS_subtypes)
for t, n in count.items():
        print(f"Subtype #{t}: {n} PUS packets.")


print("--------------------------------------------------------------")
print("APID ", target_APID, " is ", len(raw_target_APID_data), " bytes long.")
print("--------------------------------------------------------------")

# Write to file
raw_target_APID_data.tofile("raw_data.bin")
