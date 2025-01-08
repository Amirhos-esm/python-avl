import socket
import binascii
import traceback
import socket
import ssl

from avl import *

server_ip  = "172.16.21.11"
server_port = 8443


imei = "000019249153409"
# imei = "000019249152872"

IGNITION = 239
MOVEMENT = 240
DIGITAL_INPUT_1 = 1
DIGITAL_OUTPUT_1 = 179
ANALOG_INPUT_1 = 9
GNSS_STATUS = 69
GSM_SIGNAL = 21
UNPLUG_SIGNAL = 252  #// refere teltonika io element
BATTERY_VOL = 67
EXTERNAL_VOL = 66
NETWORK_TYPE = 237
BATTERY_PERCENT = 113
PITCH  = 161
HDOP  = 182
PDOP  = 181
TEMPERATURE = 53
JAMMING = 249

def convert_imei(imei:str) ->bytearray:
    imei_length = len(imei)
    imei_hex = imei.encode().hex()
    out = bytearray();
    out.append(0);
    out.append(imei_length);
    out.extend(imei.encode('utf-8'))

    return out

# Example usage:
# imei = "356307042441013"
formatted_imei = convert_imei(imei)
print(binascii.hexlify(formatted_imei,sep=" ").decode('utf-8').upper())

coordinates = getCoordinates("mc60.txt")
print(f'total of {len(coordinates[80:])} points')

# 35.74193544252437, 51.49970678861785

# Example usage:
gps_data = Gps_Element_t(
    latitude=35.74193544,
    longitude=51.4997067,
    altitude=0,
    angle=0,
    satellites=0,
    speed=0
)


# array = gps_data.serialize()
# hex_string = binascii.hexlify(array,sep=" ").decode('utf-8')
# print(len(array),"-",hex_string)  # Output: "48656C6C6F"


io = Io_Element_t();
# io.event_io_id = 1;
# io.avl_add_n1(0x15,3);
# io.avl_add_n1(239,1);
# io.avl_add_n2(0x42,0x5e0f)
# io.avl_add_n4(0xf1,0x601a)
# io.avl_add_n8(0x4e,0)


avl_data  = Avl_Data_t(gps=gps_data,io=io)
avl_data.priority = Priority_t.HIGH




#

# Create a socket object

# Create a default SSL context
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
# Server details
host = server_ip  
port = server_port           
# Create a raw socket
with socket.create_connection((host, port)) as raw_socket:
    # Wrap the socket with SSL/TLS
    with context.wrap_socket(raw_socket, server_hostname=host) as client_socket:

        print(f"Connected to {host}:{port} with {client_socket.version()}")
        try:
            # Connect to the server
            # client_socket.connect((server_ip, server_port))
            # print("Connected to the server.")

            # # Send data to the server
            # message = "Hello, server!"
            client_socket.send(formatted_imei)

            # # Receive data from the server
            
            data = client_socket.recv(1024)
            print(f"Received from server: ",binascii.hexlify(data,sep=" ").decode('utf-8').upper())

            val = True
            cc = 0;
            xx = 30
                # # Receive data from the server
            for x in coordinates[95:]:
                # print(x)
                io = Io_Element_t();
                avl_data  = Avl_Data_t(gps=gps_data,io=io)
                avl_data.priority = Priority_t.HIGH

                gps_data.latitude = x.lat
                gps_data.longitude = x.lon
                gps_data.speed = int(x.speed)
                # gps_data.speed = 0
                # avl_data.timestamp =int(x.timestamp.timestamp() * 1000);
                avl_data.timestamp = get_unix_time_difference_in_milliseconds()
                gps_data.angle = int(x.course);
                gps_data.satellites = 15
                gps_data.altitude = 1040

                # gps_data.angle = int(0);
                # gps_data.satellites = int(0)
                # gps_data.altitude = int(0)
                # gps_data.latitude = int(0)
                # gps_data.longitude = int(0)
                # gps_data.speed = int(0);
                # io.avl_add_n2(66,12000);
                # io.avl_add_n2(67,13000)
                
                val  = not val;
            

                xx = xx - 1
                # io.avl_add_n1(NETWORK_TYPE, 1);
                
                # io.avl_add_n2(ANALOG_INPUT_1,300);
                # io.avl_add_n2(BATTERY_VOL, 12000);     
                
                io.avl_add_n2(EXTERNAL_VOL, 10000);           
                io.avl_add_n2(HDOP, 300);
                io.avl_add_n2(PDOP, 300);
                io.avl_add_n1(GSM_SIGNAL, 5); 
                io.avl_add_n1(200, 3);
                io.avl_add_n1(IGNITION, 0);
                io.avl_add_n1(DIGITAL_INPUT_1, 1);
                io.avl_add_n1(DIGITAL_OUTPUT_1, 0);
                io.avl_add_n2(BATTERY_PERCENT, 18);
                io.avl_add_n1(JAMMING, 1); 
                io.avl_add_n1(PITCH, 5);
        
                
                io.avl_add_n1(GNSS_STATUS,1);
                io.avl_add_n1(UNPLUG_SIGNAL,0); 
                # if cc >= 10 and cc < 20:
                #     io.avl_add_n1(PITCH, 16);
                #     io.avl_add_n1(MOVEMENT, 0);
                #     # io.avl_add_n1(IGNITION, 1);
                #     # print("MOVEMENT 0")
                #     # io.avl_add_n1(DIGITAL_INPUT_1, 0);
                #     # io.avl_add_n1(DIGITAL_OUTPUT_1, 0);
                #     # io.avl_add_n2(BATTERY_PERCENT, 4);
                #     # io.avl_add_n1(JAMMING, 1);
                #     io.avl_add_n1(UNPLUG_SIGNAL,0);
                # else :
                #     io.avl_add_n1(JAMMING, 0);
                #     io.avl_add_n1(UNPLUG_SIGNAL,1);
                #     io.avl_add_n1(PITCH, 5);
                #     io.avl_add_n1(MOVEMENT, 1);
                #     # io.avl_add_n1(IGNITION, 0);
                #     # io.avl_add_n1(DIGITAL_INPUT_1, 1);
                #     # io.avl_add_n1(DIGITAL_OUTPUT_1, 1);
                #     # io.avl_add_n2(BATTERY_PERCENT, 18);
                cc += 1
                
                io.avl_add_n1(TEMPERATURE, 30);


                io = Io_Element_t();

                print(avl_data.timestamp)
                client_socket.send(avl_data.serialize())
                print(binascii.hexlify(avl_data.serialize(),sep=" ").decode('utf-8').upper())
                
                data = client_socket.recv(1024)
                print(f"Received from server: ",binascii.hexlify(data,sep=" ").decode('utf-8').upper())
                time.sleep(1);
            

        except ConnectionRefusedError:
            print("Connection to the server was refused.")
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred: {e}")
        finally:
            # Close the socket
            client_socket.close()
            print("Socket closed.")
