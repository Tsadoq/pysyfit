import os
import struct
import datetime
from typing import Dict, List, Optional
from io import BytesIO

from pysyfit.models.enum_types import FileType, SubSport, Sport, WorkoutStepDurationType, WorkoutStepTargetType, \
    Intensity
from pysyfit.models.workout_models import Workout, FileIdMessage, WorkoutMessage, WorkoutStep
from pysyfit.utils.timestamp_utils import datetime_to_fit_timestamp


def read_fit_file(file_path: str) -> Workout:
    """
    Read a FIT file and convert it to a Workout object.
    :param file_path: Path to the FIT file
    :return: Workout object containing the parsed data
    """
    from fitparse import FitFile

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"FIT file not found: {file_path}")

    try:
        fit_file = FitFile(file_path)
        fit_file.parse()
    except Exception as e:
        raise ValueError(f"Error parsing FIT file: {e}")

    file_id_msgs = list(fit_file.get_messages('file_id'))
    workout_msgs = list(fit_file.get_messages('workout'))
    workout_step_msgs = list(fit_file.get_messages('workout_step'))

    if not file_id_msgs:
        raise ValueError("FIT file does not contain a file_id message")
    if not workout_msgs:
        raise ValueError("FIT file does not contain a workout message")
    if not workout_step_msgs:
        raise ValueError("FIT file does not contain any workout_step messages")

    file_id_data = file_id_msgs[0].get_values()

    file_type = file_id_data.get('type', FileType.WORKOUT)
    if isinstance(file_type, str) and file_type.lower() == 'workout':
        file_type = FileType.WORKOUT

    manufacturer = file_id_data.get('manufacturer', 0)

    file_id = FileIdMessage(
        type=file_type,
        manufacturer=manufacturer,
        product=file_id_data.get('product', 0),
        serial_number=file_id_data.get('serial_number'),
        time_created=file_id_data.get('time_created', None),
        number=file_id_data.get('number')
    )

    workout_data = workout_msgs[0].get_values()
    workout = WorkoutMessage(
        wkt_name=workout_data.get('wkt_name', ''),
        sport=Sport(workout_data.get('sport', Sport.GENERIC)),
        sub_sport=SubSport(workout_data.get('sub_sport', SubSport.GENERIC)),
        num_valid_steps=workout_data.get('num_valid_steps', len(workout_step_msgs))
    )

    steps = []
    for step_msg in workout_step_msgs:
        step_data = step_msg.get_values()

        duration_type_value = step_data.get('duration_type', WorkoutStepDurationType.TIME)
        if isinstance(duration_type_value, str):
            duration_type_map = {
                'time': WorkoutStepDurationType.TIME,
                'distance': WorkoutStepDurationType.DISTANCE,
                'hr_less_than': WorkoutStepDurationType.HR_LESS_THAN,
                'hr_greater_than': WorkoutStepDurationType.HR_GREATER_THAN,
                'calories': WorkoutStepDurationType.CALORIES,
                'open': WorkoutStepDurationType.OPEN,
                'repeat_until_steps_cmplt': WorkoutStepDurationType.REPEAT_UNTIL_STEPS_CMPLT,
                'repeat': WorkoutStepDurationType.REPEAT_UNTIL_STEPS_CMPLT,
                'repeat_until_time': WorkoutStepDurationType.REPEAT_UNTIL_TIME,
                'repeat_until_distance': WorkoutStepDurationType.REPEAT_UNTIL_DISTANCE,
                'repeat_until_calories': WorkoutStepDurationType.REPEAT_UNTIL_CALORIES,
                'repeat_until_hr_less_than': WorkoutStepDurationType.REPEAT_UNTIL_HR_LESS_THAN,
                'repeat_until_hr_greater_than': WorkoutStepDurationType.REPEAT_UNTIL_HR_GREATER_THAN,
                'repeat_until_power_less_than': WorkoutStepDurationType.REPEAT_UNTIL_POWER_LESS_THAN,
                'repeat_until_power_greater_than': WorkoutStepDurationType.REPEAT_UNTIL_POWER_GREATER_THAN,
                'power_less_than': WorkoutStepDurationType.POWER_LESS_THAN,
                'power_greater_than': WorkoutStepDurationType.POWER_GREATER_THAN,
                'repetition_time': WorkoutStepDurationType.REPETITION_TIME
            }
            duration_type = duration_type_map.get(duration_type_value.lower(), WorkoutStepDurationType.TIME)
        else:
            duration_type = WorkoutStepDurationType(duration_type_value)

        duration_value = step_data.get('duration_value')

        duration_time = None
        duration_distance = None
        duration_hr = None
        duration_calories = None
        duration_step = None
        duration_power = None

        if duration_type == WorkoutStepDurationType.TIME:
            duration_time = duration_value
        elif duration_type == WorkoutStepDurationType.DISTANCE:
            duration_distance = duration_value
        elif duration_type in [WorkoutStepDurationType.HR_LESS_THAN, WorkoutStepDurationType.HR_GREATER_THAN]:
            duration_hr = duration_value
        elif duration_type == WorkoutStepDurationType.CALORIES:
            duration_calories = duration_value
        elif duration_type in [WorkoutStepDurationType.REPEAT_UNTIL_STEPS_CMPLT]:
            duration_step = duration_value
        elif duration_type in [WorkoutStepDurationType.POWER_LESS_THAN, WorkoutStepDurationType.POWER_GREATER_THAN]:
            duration_power = duration_value

        target_type_value = step_data.get('target_type', WorkoutStepTargetType.OPEN)
        if isinstance(target_type_value, str):
            target_type_map = {
                'speed': WorkoutStepTargetType.SPEED,
                'heart_rate': WorkoutStepTargetType.HEART_RATE,
                'open': WorkoutStepTargetType.OPEN,
                'cadence': WorkoutStepTargetType.CADENCE,
                'power': WorkoutStepTargetType.POWER,
                'grade': WorkoutStepTargetType.GRADE,
                'resistance': WorkoutStepTargetType.RESISTANCE,
                'power_3s': WorkoutStepTargetType.POWER_3S,
                'power_10s': WorkoutStepTargetType.POWER_10S,
                'power_30s': WorkoutStepTargetType.POWER_30S,
                'power_lap': WorkoutStepTargetType.POWER_LAP,
                'swim_stroke': WorkoutStepTargetType.SWIM_STROKE,
                'speed_lap': WorkoutStepTargetType.SPEED_LAP,
                'heart_rate_lap': WorkoutStepTargetType.HEART_RATE_LAP
            }
            target_type = target_type_map.get(target_type_value.lower(), WorkoutStepTargetType.OPEN)
        else:
            target_type = WorkoutStepTargetType(target_type_value)

        target_value = step_data.get('target_value')

        target_hr_zone = None
        target_power_zone = None
        target_stroke_type = None
        target_speed_zone = None
        target_cadence_zone = None

        if target_type == WorkoutStepTargetType.HEART_RATE:
            target_hr_zone = target_value
        elif target_type == WorkoutStepTargetType.POWER:
            target_power_zone = target_value
        elif target_type == WorkoutStepTargetType.CADENCE:
            target_cadence_zone = target_value
        elif target_type == WorkoutStepTargetType.SPEED:
            target_speed_zone = target_value
        elif target_type == WorkoutStepTargetType.SWIM_STROKE:
            target_stroke_type = target_value

        custom_target_heart_rate_low = step_data.get('custom_target_heart_rate_low')
        custom_target_heart_rate_high = step_data.get('custom_target_heart_rate_high')
        custom_target_power_low = step_data.get('custom_target_power_low')
        custom_target_power_high = step_data.get('custom_target_power_high')
        custom_target_speed_low = step_data.get('custom_target_speed_low')
        custom_target_speed_high = step_data.get('custom_target_speed_high')
        custom_target_cadence_low = step_data.get('custom_target_cadence_low')
        custom_target_cadence_high = step_data.get('custom_target_cadence_high')

        intensity_value = step_data.get('intensity', Intensity.ACTIVE)
        if isinstance(intensity_value, str):
            intensity_map = {
                'active': Intensity.ACTIVE,
                'rest': Intensity.REST,
                'warmup': Intensity.WARMUP,
                'cooldown': Intensity.COOLDOWN
            }
            intensity = intensity_map.get(intensity_value.lower(), Intensity.ACTIVE)
        else:
            intensity = Intensity(intensity_value)

        step = WorkoutStep(
            message_index=step_data.get('message_index', 0),
            wkt_step_name=step_data.get('wkt_step_name'),
            intensity=intensity,
            notes=step_data.get('notes'),
            duration_type=duration_type,
            duration_value=duration_value,
            duration_time=duration_time,
            duration_distance=duration_distance,
            duration_hr=duration_hr,
            duration_calories=duration_calories,
            duration_step=duration_step,
            duration_power=duration_power,
            target_type=target_type,
            target_value=target_value,
            target_hr_zone=target_hr_zone,
            target_power_zone=target_power_zone,
            target_stroke_type=target_stroke_type,
            target_speed_zone=target_speed_zone,
            target_cadence_zone=target_cadence_zone,
            custom_target_heart_rate_low=custom_target_heart_rate_low,
            custom_target_heart_rate_high=custom_target_heart_rate_high,
            custom_target_power_low=custom_target_power_low,
            custom_target_power_high=custom_target_power_high,
            custom_target_speed_low=custom_target_speed_low,
            custom_target_speed_high=custom_target_speed_high,
            custom_target_cadence_low=custom_target_cadence_low,
            custom_target_cadence_high=custom_target_cadence_high
        )

        steps.append(step)

    return Workout(
        file_id=file_id,
        workout=workout,
        steps=steps
    )


def write_fit_file(workout: Workout, file_path: str) -> None:
    """
    Write a Workout object to a FIT file using direct binary encoding.
    This implementation follows the FIT protocol specification exactly.

    :param workout: The Workout object to write
    :param file_path: Path where the FIT file should be written
    :return: None
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    # Create a buffer to write the FIT file
    buffer = BytesIO()

    # FIT file constants
    FIT_HEADER_SIZE = 14
    FIT_PROTOCOL_VERSION = 16
    FIT_PROFILE_VERSION = 1320
    FIT_DATA_TYPE = b'.FIT'

    # Message types (global message numbers)
    FILE_ID_MSG_NUM = 0
    WORKOUT_MSG_NUM = 26
    WORKOUT_STEP_MSG_NUM = 27

    # Local message types
    FILE_ID_LOCAL_MSG_NUM = 0
    WORKOUT_LOCAL_MSG_NUM = 1
    WORKOUT_STEP_LOCAL_MSG_NUM = 2

    # FIT Base Types
    BASE_TYPE_ENUM = 0x00
    BASE_TYPE_SINT8 = 0x01
    BASE_TYPE_UINT8 = 0x02
    BASE_TYPE_SINT16 = 0x83
    BASE_TYPE_UINT16 = 0x84
    BASE_TYPE_SINT32 = 0x85
    BASE_TYPE_UINT32 = 0x86
    BASE_TYPE_STRING = 0x07
    BASE_TYPE_FLOAT32 = 0x88
    BASE_TYPE_FLOAT64 = 0x89
    BASE_TYPE_UINT8Z = 0x0A
    BASE_TYPE_UINT16Z = 0x8B
    BASE_TYPE_UINT32Z = 0x8C
    BASE_TYPE_BYTE = 0x0D
    BASE_TYPE_SINT64 = 0x8E
    BASE_TYPE_UINT64 = 0x8F
    BASE_TYPE_UINT64Z = 0x90

    # CRC16 table for calculating FIT file CRC
    CRC16_TABLE = [
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
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
        0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0,
    ]

    def calculate_crc(data, crc=0):
        """
        Calculate CRC16 for FIT files.

        Args:
            data: Bytes data for calculating CRC
            crc: Initial CRC value (default: 0)

        Returns:
            Calculated CRC16 value
        """
        for byte in data:
            crc = ((crc << 8) & 0xff00) ^ CRC16_TABLE[((crc >> 8) & 0xff) ^ byte]
        return crc & 0xffff

    # Write header with placeholders for data_size and CRC
    buffer.write(struct.pack(
        '<BBHI4sH',
        FIT_HEADER_SIZE,
        FIT_PROTOCOL_VERSION,
        FIT_PROFILE_VERSION,
        0,  # data_size placeholder
        FIT_DATA_TYPE,
        0  # CRC placeholder
    ))

    # Mark the start of data
    data_start_pos = buffer.tell()

    # Write File ID definition message
    buffer.write(struct.pack('<B', 0x40 | FILE_ID_LOCAL_MSG_NUM))  # Definition message header
    buffer.write(struct.pack('<B', 0))  # Reserved
    buffer.write(struct.pack('<B', 0))  # Architecture (0 = little endian)
    buffer.write(struct.pack('<H', FILE_ID_MSG_NUM))  # Global message number (0 = File ID)
    buffer.write(struct.pack('<B', 5))  # Number of fields

    # Field definitions for File ID message
    buffer.write(struct.pack('<BBB', 0, 1, BASE_TYPE_ENUM))  # Field 0: type (enum)
    buffer.write(struct.pack('<BBB', 1, 2, BASE_TYPE_UINT16))  # Field 1: manufacturer (uint16)
    buffer.write(struct.pack('<BBB', 2, 2, BASE_TYPE_UINT16))  # Field 2: product (uint16)
    buffer.write(struct.pack('<BBB', 3, 4, BASE_TYPE_UINT32Z))  # Field 3: serial_number (uint32z)
    buffer.write(struct.pack('<BBB', 4, 4, BASE_TYPE_UINT32))  # Field 4: time_created (uint32)

    # File ID data message
    fit_timestamp = datetime_to_fit_timestamp(
        workout.file_id.time_created) if workout.file_id.time_created else datetime_to_fit_timestamp(
        datetime.datetime.now())
    buffer.write(struct.pack('<B', 0x00 | FILE_ID_LOCAL_MSG_NUM))  # Data message header
    buffer.write(struct.pack('<B', int(workout.file_id.type)))  # Field 0: type
    buffer.write(struct.pack('<H',
                             workout.file_id.manufacturer if workout.file_id.manufacturer is not None else 0))  # Field 1: manufacturer
    buffer.write(
        struct.pack('<H', workout.file_id.product if workout.file_id.product is not None else 0))  # Field 2: product
    buffer.write(struct.pack('<I',
                             workout.file_id.serial_number if workout.file_id.serial_number is not None else 0))  # Field 3: serial_number
    buffer.write(struct.pack('<I', fit_timestamp))  # Field 4: time_created

    # Write Workout definition message
    buffer.write(struct.pack('<B', 0x40 | WORKOUT_LOCAL_MSG_NUM))  # Definition message header
    buffer.write(struct.pack('<B', 0))  # Reserved
    buffer.write(struct.pack('<B', 0))  # Architecture (0 = little endian)
    buffer.write(struct.pack('<H', WORKOUT_MSG_NUM))  # Global message number (26 = Workout)
    buffer.write(struct.pack('<B', 4))  # Number of fields

    # Field definitions for Workout message
    buffer.write(struct.pack('<BBB', 4, 1, BASE_TYPE_ENUM))  # Field 4: sport (enum)
    buffer.write(struct.pack('<BBB', 5, 4, BASE_TYPE_UINT32Z))  # Field 5: capabilities (uint32z)
    buffer.write(struct.pack('<BBB', 6, 2, BASE_TYPE_UINT16))  # Field 6: num_valid_steps (uint16)
    buffer.write(struct.pack('<BBB', 8, 16, BASE_TYPE_STRING))  # Field 8: wkt_name (string)

    # Workout data message
    workout_name = workout.workout.wkt_name if workout.workout.wkt_name else "Workout"
    workout_name_bytes = workout_name.encode('utf-8')[:16].ljust(16, b'\0')
    buffer.write(struct.pack('<B', 0x00 | WORKOUT_LOCAL_MSG_NUM))  # Data message header
    buffer.write(struct.pack('<B', int(workout.workout.sport)))  # Field 4: sport
    buffer.write(struct.pack('<I', 0))  # Field 5: capabilities (default to 0)
    buffer.write(struct.pack('<H', len(workout.steps)))  # Field 6: num_valid_steps
    buffer.write(workout_name_bytes)  # Field 8: wkt_name

    # Write Workout Step definition message
    buffer.write(struct.pack('<B', 0x40 | WORKOUT_STEP_LOCAL_MSG_NUM))  # Definition message header
    buffer.write(struct.pack('<B', 0))  # Reserved
    buffer.write(struct.pack('<B', 0))  # Architecture (0 = little endian)
    buffer.write(struct.pack('<H', WORKOUT_STEP_MSG_NUM))  # Global message number (27 = Workout Step)
    buffer.write(struct.pack('<B', 7))  # Number of fields

    # Field definitions for Workout Step message
    buffer.write(struct.pack('<BBB', 254, 2, BASE_TYPE_UINT16))  # Field 254: message_index (uint16)
    buffer.write(struct.pack('<BBB', 0, 16, BASE_TYPE_STRING))  # Field 0: wkt_step_name (string)
    buffer.write(struct.pack('<BBB', 1, 1, BASE_TYPE_ENUM))  # Field 1: duration_type (enum)
    buffer.write(struct.pack('<BBB', 2, 4, BASE_TYPE_UINT32))  # Field 2: duration_value (uint32)
    buffer.write(struct.pack('<BBB', 3, 1, BASE_TYPE_ENUM))  # Field 3: intensity (enum)
    buffer.write(struct.pack('<BBB', 4, 1, BASE_TYPE_ENUM))  # Field 4: target_type (enum)
    buffer.write(struct.pack('<BBB', 5, 4, BASE_TYPE_UINT32))  # Field 5: target_value (uint32)

    # Write Workout Step messages
    for step in workout.steps:
        # Get duration value based on duration type
        duration_value = step.duration_value
        if duration_value is None:
            if step.duration_type == WorkoutStepDurationType.TIME and step.duration_time is not None:
                duration_value = int(step.duration_time * 1000)  # Convert seconds to milliseconds
            elif step.duration_type == WorkoutStepDurationType.DISTANCE and step.duration_distance is not None:
                duration_value = int(step.duration_distance * 100)  # Convert meters to centimeters
            elif step.duration_type in [WorkoutStepDurationType.HR_LESS_THAN,
                                        WorkoutStepDurationType.HR_GREATER_THAN] and step.duration_hr is not None:
                duration_value = int(step.duration_hr)
            elif step.duration_type == WorkoutStepDurationType.CALORIES and step.duration_calories is not None:
                duration_value = int(step.duration_calories)
            elif step.duration_type in [
                WorkoutStepDurationType.REPEAT_UNTIL_STEPS_CMPLT] and step.duration_step is not None:
                duration_value = int(step.duration_step)
            elif step.duration_type in [WorkoutStepDurationType.POWER_LESS_THAN,
                                        WorkoutStepDurationType.POWER_GREATER_THAN] and step.duration_power is not None:
                duration_value = int(step.duration_power)
            else:
                duration_value = 0
        else:
            # Ensure duration_value is an integer
            duration_value = int(duration_value)

        # Get target value
        target_value = step.target_value
        if target_value is None:
            if step.target_type == WorkoutStepTargetType.HEART_RATE and step.target_hr_zone is not None:
                target_value = int(step.target_hr_zone)
            elif step.target_type == WorkoutStepTargetType.POWER and step.target_power_zone is not None:
                target_value = int(step.target_power_zone)
            elif step.target_type == WorkoutStepTargetType.CADENCE and step.target_cadence_zone is not None:
                target_value = int(step.target_cadence_zone)
            elif step.target_type == WorkoutStepTargetType.SPEED and step.target_speed_zone is not None:
                target_value = int(step.target_speed_zone)
            else:
                target_value = 0
        else:
            # Ensure target_value is an integer
            target_value = int(target_value)

        # Get step name
        step_name = step.wkt_step_name if step.wkt_step_name else ""
        step_name_bytes = step_name.encode('utf-8')[:16].ljust(16, b'\0')

        # Write Workout Step data message
        buffer.write(struct.pack('<B', 0x00 | WORKOUT_STEP_LOCAL_MSG_NUM))  # Data message header
        buffer.write(
            struct.pack('<H', step.message_index if step.message_index is not None else 0))  # Field 254: message_index
        buffer.write(step_name_bytes)  # Field 0: wkt_step_name
        buffer.write(struct.pack('<B', int(step.duration_type)))  # Field 1: duration_type
        buffer.write(struct.pack('<I', duration_value))  # Field 2: duration_value
        buffer.write(struct.pack('<B', int(step.intensity)))  # Field 3: intensity
        buffer.write(struct.pack('<B', int(step.target_type)))  # Field 4: target_type
        buffer.write(struct.pack('<I', target_value))  # Field 5: target_value

    # Calculate data size
    data_end_pos = buffer.tell()
    data_size = data_end_pos - data_start_pos

    # Update data size in header
    buffer.seek(4)
    buffer.write(struct.pack('<I', data_size))

    # Calculate header CRC
    buffer.seek(0)
    header_bytes = buffer.read(12)
    header_crc = calculate_crc(header_bytes)

    # Update header CRC
    buffer.seek(12)
    buffer.write(struct.pack('<H', header_crc))

    # Calculate file CRC
    buffer.seek(data_start_pos)
    file_bytes = buffer.read(data_size)
    file_crc = calculate_crc(file_bytes, crc=header_crc)

    # Write file CRC
    buffer.seek(data_end_pos)
    buffer.write(struct.pack('<H', file_crc))

    # Write buffer to file
    with open(file_path, 'wb') as f:
        buffer.seek(0)
        f.write(buffer.getvalue())
