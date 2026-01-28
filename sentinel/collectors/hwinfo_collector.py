"""
HWiNFO64 integration collector (Free alternative to AIDA64)
Collects data from HWiNFO64 shared memory
"""
import struct
import mmap
from typing import Dict, Any, Optional
from .base import BaseCollector


class HWiNFOCollector(BaseCollector):
    """Collects data from HWiNFO64 shared memory"""
    
    # HWiNFO shared memory structure constants
    HWINFO_SENSORS_SM2_SIGNATURE = 0x32534948  # 'HIS2'
    HWINFO_SENSORS_STRING_LEN = 128
    HWINFO_UNIT_STRING_LEN = 16
    
    def __init__(self):
        super().__init__("HWiNFO64")
        self.shared_memory = None
        self._initialize_shared_memory()
    
    def _initialize_shared_memory(self):
        """Initialize connection to HWiNFO shared memory"""
        try:
            # Try to open HWiNFO shared memory
            self.shared_memory = mmap.mmap(
                -1,
                0,
                "Global\\HWiNFO_SENS_SM2",
                access=mmap.ACCESS_READ
            )
        except Exception:
            self.shared_memory = None
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Collect data from HWiNFO shared memory"""
        if not self.shared_memory:
            self._initialize_shared_memory()
            if not self.shared_memory:
                return None
        
        try:
            # Read shared memory header
            self.shared_memory.seek(0)
            
            # Verify signature
            signature = struct.unpack('I', self.shared_memory.read(4))[0]
            if signature != self.HWINFO_SENSORS_SM2_SIGNATURE:
                return None
            
            # Read version and revision
            version = struct.unpack('I', self.shared_memory.read(4))[0]
            revision = struct.unpack('q', self.shared_memory.read(8))[0]
            
            # Read poll time
            poll_time = struct.unpack('q', self.shared_memory.read(8))[0]
            
            # Read offsets
            offset_of_sensor_section = struct.unpack('I', self.shared_memory.read(4))[0]
            size_of_sensor_element = struct.unpack('I', self.shared_memory.read(4))[0]
            num_sensor_elements = struct.unpack('I', self.shared_memory.read(4))[0]
            
            offset_of_reading_section = struct.unpack('I', self.shared_memory.read(4))[0]
            size_of_reading_element = struct.unpack('I', self.shared_memory.read(4))[0]
            num_reading_elements = struct.unpack('I', self.shared_memory.read(4))[0]
            
            # Collect sensor readings
            sensors = {}
            
            for i in range(num_reading_elements):
                # Seek to reading element
                offset = offset_of_reading_section + (i * size_of_reading_element)
                self.shared_memory.seek(offset)
                
                # Read reading data
                reading_type = struct.unpack('I', self.shared_memory.read(4))[0]
                sensor_index = struct.unpack('I', self.shared_memory.read(4))[0]
                reading_id = struct.unpack('I', self.shared_memory.read(4))[0]
                
                # Read label
                label_bytes = self.shared_memory.read(self.HWINFO_SENSORS_STRING_LEN * 2)
                label = label_bytes.decode('utf-16-le', errors='ignore').rstrip('\x00')
                
                # Read unit
                unit_bytes = self.shared_memory.read(self.HWINFO_UNIT_STRING_LEN * 2)
                unit = unit_bytes.decode('utf-16-le', errors='ignore').rstrip('\x00')
                
                # Read value
                value = struct.unpack('d', self.shared_memory.read(8))[0]
                
                # Read min/max/avg
                value_min = struct.unpack('d', self.shared_memory.read(8))[0]
                value_max = struct.unpack('d', self.shared_memory.read(8))[0]
                value_avg = struct.unpack('d', self.shared_memory.read(8))[0]
                
                # Store sensor reading
                if label and value != 0:
                    sensor_key = label.replace(' ', '_').replace('/', '_')
                    sensors[sensor_key] = {
                        'value': value,
                        'unit': unit,
                        'min': value_min,
                        'max': value_max,
                        'avg': value_avg,
                        'type': reading_type
                    }
            
            # Organize by category
            data = {
                'temperatures': {},
                'voltages': {},
                'fans': {},
                'power': {},
                'clocks': {},
                'usage': {},
                'other': {}
            }
            
            for key, sensor in sensors.items():
                unit = sensor['unit'].lower()
                value = sensor['value']
                
                if '°c' in unit or 'temp' in key.lower():
                    data['temperatures'][key] = value
                elif 'v' == unit or 'volt' in key.lower():
                    data['voltages'][key] = value
                elif 'rpm' in unit or 'fan' in key.lower():
                    data['fans'][key] = value
                elif 'w' == unit or 'power' in key.lower():
                    data['power'][key] = value
                elif 'mhz' in unit or 'clock' in key.lower():
                    data['clocks'][key] = value
                elif '%' in unit or 'usage' in key.lower():
                    data['usage'][key] = value
                else:
                    data['other'][key] = value
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error reading HWiNFO shared memory: {e}")
            return None
    
    def __del__(self):
        """Cleanup shared memory"""
        if self.shared_memory:
            try:
                self.shared_memory.close()
            except Exception:
                pass
