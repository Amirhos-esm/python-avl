from avl import *
import binascii

# Example usage:
gps_data = Gps_Element_t(
    latitude=35.0,
    longitude=35.0,
    altitude=0,
    angle=95,
    satellites=0,
    speed=0
)

# array = gps_data.serialize()
# hex_string = binascii.hexlify(array,sep=" ").decode('utf-8')
# print(len(array),"-",hex_string)  # Output: "48656C6C6F"


io = Io_Element_t();
# io.event_io_id = 1;
# io.avl_add_n1(0x15,3);
# io.avl_add_n1(1,1);
# io.avl_add_n2(0x42,0x5e0f)
# io.avl_add_n4(0xf1,0x601a)
# io.avl_add_n8(0x4e,0)


avl_data  = Avl_Data_t(gps=gps_data,io=io)
avl_data.priority = Priority_t.HIGH
avl_data.timestamp =  1695118888
# print(io)
array = avl_data.serialize()
hex_string = binascii.hexlify(array,sep=" ").decode('utf-8').upper()
print(len(array),"-",hex_string)  # Output: "48656C6C6F"