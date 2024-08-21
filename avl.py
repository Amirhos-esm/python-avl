from pydantic import BaseModel, Field, conint, confloat  
from typing import List
from enum import Enum
import struct
import time
import pynmea2
from datetime import datetime
import pytz

def get_unix_time_difference_in_milliseconds():
    current_time_seconds = time.time()
    current_time_milliseconds = int(current_time_seconds * 1000)
    return current_time_milliseconds

class Priority_t(int, Enum):
    LOW = 0
    HIGH = 1
    PANIC = 2
    def serialize(self) -> bytes:
        return struct.pack("B", self.priority.value)
    def deserialize(serialized_data: bytes):
        deserialized_data = struct.unpack("B", serialized_data)
        return Priority_t(deserialized_data[0])

class Gps_Element_t(BaseModel):
    latitude: confloat(ge=-90, le=90) = 0  # Decimal degree, between -90 and 90
    longitude: confloat(ge=-180, le=180) = 0  # Decimal degree, between -180 and 180
    altitude: conint(ge=0) = 0
    angle: conint(ge=0, le=65535) = 0  # Assuming the angle range
    satellites: conint(ge=0, le=255) = 0
    speed: conint(ge=0, le=65535) = 0 # Assuming the speed range
    def serialize(data):
        # Define the format string for struct.pack
        format_string = ">i i H H B H"  # i for int32, H for uint16, and B for uint8

        # Pack the data into a binary string
        binary_data = struct.pack(
            format_string,
            int(data.longitude * 1e7) - 1,
            int(data.latitude * 1e7) + 1,
            data.altitude,
            data.angle,
            data.satellites,
            data.speed
        )
        return bytearray(binary_data)


class Io_Element_t(BaseModel):
    event_io_id: conint(ge=0, le=255) = 0
    n_of_n1: conint(ge=0, le=16) = 0
    n1_id: List[conint(ge=0, le=255)] = Field(..., min_items=16, max_items=16, default_factory=list)
    n1: List[conint(ge=0, le=255)] = Field(..., min_items=16, max_items=16, default_factory=list)
    n_of_n2: conint(ge=0, le=8) = 0
    n2_id: List[conint(ge=0, le=255)] = Field(..., min_items=8, max_items=8, default_factory=list)
    n2: List[conint(ge=0, le=65535)] = Field(..., min_items=8, max_items=8, default_factory=list)
    n_of_n4: conint(ge=0, le=4) = 0
    n4_id: List[conint(ge=0, le=255)] = Field(..., min_items=4, max_items=4, default_factory=list)
    n4: List[conint(ge=0, le=4294967295)] = Field(..., min_items=4, max_items=4, default_factory=list)
    n_of_n8: conint(ge=0, le=2) = 0
    n8_id: List[conint(ge=0, le=255)] = Field(..., min_items=2, max_items=2, default_factory=list)
    n8: List[conint(ge=0, le=18446744073709551615)] = Field(..., min_items=2, max_items=2, default_factory=list)

    def serialize(data):
        serialized_data = bytearray()
        
        # io elements
        serialized_data.append(data.event_io_id)
        sum_n1_n2_n4_n8 = data.n_of_n1 + data.n_of_n2 + data.n_of_n4 + data.n_of_n8
        serialized_data.append(sum_n1_n2_n4_n8)
        
        # n1
        serialized_data.append(data.n_of_n1)
        for i in range(data.n_of_n1):
            serialized_data.append(data.n1_id[i])
            serialized_data.append(data.n1[i])
        
        # n2
        serialized_data.append(data.n_of_n2)
        for i in range(data.n_of_n2):
            serialized_data.append(data.n2_id[i])
            serialized_data.extend(struct.pack('>H', data.n2[i]))  # Use struct.pack for big-endian uint16
        
        # n4
        serialized_data.append(data.n_of_n4)
        for i in range(data.n_of_n4):
            serialized_data.append(data.n4_id[i])
            serialized_data.extend(struct.pack('>I', data.n4[i]))  # Use struct.pack for big-endian uint32
        
        # n8
        serialized_data.append(data.n_of_n8)
        for i in range(data.n_of_n8):
            serialized_data.append(data.n8_id[i])
            serialized_data.extend(struct.pack('>Q', data.n8[i]))  # Use struct.pack for big-endian uint64
        
        return serialized_data
    def avl_add_n1(self, io_id, io_value):
        # if self.n_of_n1 >= len(self.n1_id):
        #     return False
        self.n1_id.append(io_id) 
        self.n1.append(io_value)
        self.n_of_n1 += 1
        return True

    def avl_add_n2(self, io_id, io_value):
        # if self.n_of_n2 >= len(self.n2_id):
        #     return False
        self.n2_id.append(io_id) 
        self.n2.append(io_value)
        self.n_of_n2 += 1
        return True

    def avl_add_n4(self, io_id, io_value):
        # if self.n_of_n4 >= len(self.n4_id):
        #     return False
        self.n4_id.append(io_id) 
        self.n4.append(io_value)
        self.n_of_n4 += 1
        return True

    def avl_add_n8(self, io_id, io_value):
        # if self.n_of_n8 >= len(self.n8_id):
        #     return False
        self.n8_id.append(io_id) 
        self.n8.append(io_value)
        self.n_of_n8 += 1
        return True


def calculate_crc16(data, start, end):
    crc = 0x0000  # Initial CRC value

    if data is None:
        return 0

    for i in range(start, end):
        crc ^= data[i]

        for k in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xa001
            else:
                crc >>= 1
    return crc
class Avl_Data_t(BaseModel):
    timestamp: conint(ge=0) = get_unix_time_difference_in_milliseconds()  # in milli seconds
    priority: Priority_t = Priority_t.LOW
    gps: Gps_Element_t = Gps_Element_t() 
    io: Io_Element_t = Io_Element_t() 
    def serialize(data):
        stream = bytearray()
        gps_array = data.gps.serialize()
        io_array = data.io.serialize();
        stream.extend(struct.pack(">I", 0))
        stream.extend(struct.pack(">I", len(io_array) + len(gps_array) + 12))
        # codec id
        startPos = len(stream)
        stream.append(0x08)
        # number of record
        stream.append(0x01)
        
        #avl data
        # Serialize the timestamp as a 64-bit unsigned integer
        stream.extend(struct.pack(">Q", data.timestamp))
        stream.append(data.priority.value)
        stream.extend(gps_array)
        stream.extend(io_array)

        stream.append(0x01)
        endPos = len(stream)

        # Calculate and write CRC16
        crc = calculate_crc16(stream, startPos, endPos)
        stream.extend(struct.pack(">I", crc))
        return stream

# class Avl_Packet_t(BaseModel):
#     avls: List[Avl_Data_t] = []
#     def serialize(data):
#         stream = bytearray()
#         gps_array = data.gps.serialize()
#         io_array = data.io.serialize();
#         stream.extend(struct.pack(">I", len(io_array) + len(gps_array) + 12))
#         # codec id
#         stream.append(0x08)
#         # number of record
#         stream.append(0x01)

#         stream.append




class GPS(BaseModel):
    timestamp: datetime = 0
    lat: float = 0
    lon: float = 0
    height: float = 0
    speed: float = 0
    course: float = 0
    is_valid: bool = False
    meta_data: dict = None

    def addMetaData(cls, key, value):
        if cls.meta_data == None:
            cls.meta_data = {}
        cls.meta_data[key] = value
    def getTuple(cls,inverse = False):
       if inverse:
           return (cls.lon,cls.lat)
       return (cls.lat,cls.lon)



def parse_rmc(rmc:str):
    try:
        msg = pynmea2.parse(rmc)

        if isinstance(msg, pynmea2.RMC):
            # Convert longitude from DMM to DD
            # msg.datestamp: date
            combined_datetime_obj = datetime(msg.datestamp.year,msg.datestamp.month,msg.datestamp.day,
                                             msg.timestamp.hour,msg.timestamp.minute,msg.timestamp.second,msg.timestamp.microsecond
                                             )
           # Set the timezone to UTC
            utc_timezone = pytz.UTC
            combined_datetime_obj = utc_timezone.localize(combined_datetime_obj)
            if msg.is_valid:
                latitude_dmm = msg.lat
                msg.lat = round(int(latitude_dmm[:2]) + float(latitude_dmm[2:]) / 60 , 7)
                longitude_dmm = msg.lon
                msg.lon = round(int(longitude_dmm[:3]) + float(longitude_dmm[3:]) / 60 , 7)
                msg.spd_over_grnd = round(msg.spd_over_grnd * 1.852 , 1 )
                return GPS(
                    is_valid=msg.is_valid,lat=msg.lat,lon=msg.lon,speed=msg.spd_over_grnd,course=msg.true_course,timestamp=combined_datetime_obj
            )
            return GPS(is_valid= False , timestamp=combined_datetime_obj)
        else:
            print("Unknown NMEA sentence type:", msg.sentence_type)
            print(rmc)
            return None
    except pynmea2.ParseError as e:
        print(rmc)  
        print("Parse error:", str(e))
        return None
    
def getCoordinates(fileName,prefix="") -> List[GPS]:
    file_contents = []
    index = 0
    with open(fileName, 'r') as file:
            # Read the entire file into a string
            file_contents = file.read().split("\n")
    coordinates = []
    for rmc in file_contents:
        if len(rmc) < 5:
            continue
        coordinates.append(parse_rmc(prefix+rmc))
        coordinates[-1].addMetaData("index",str(index))
        index+=1
    return coordinates