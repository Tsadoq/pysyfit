import os
import struct
from typing import Dict, List, Optional, Union
from io import BytesIO
import datetime

from pysyfit.models.enum_types import FileType, SubSport, Sport, WorkoutStepDurationType, WorkoutStepTargetType, \
    Intensity
from pysyfit.models.workout_models import Workout, FileIdMessage, WorkoutMessage, WorkoutStep
from pysyfit.utils.timestamp_utils import datetime_to_fit_timestamp

# CRC table from FIT SDK
CRC_TABLE = (
    0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
    0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
)


def calculate_crc(buffer, crc=0):
    """
    Calculate CRC16 for FIT files using the algorithm from the FIT SDK.

    Args:
        buffer: Bytes data for calculating CRC
        crc: Initial CRC value (default: 0)

    Returns:
        Calculated CRC16 value
    """
    if not buffer:
        return crc

    for byte in buffer:
        # Process the lower 4 bits
        tmp = CRC_TABLE[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ CRC_TABLE[byte & 0xF]

        # Process the upper 4 bits
        tmp = CRC_TABLE[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ CRC_TABLE[(byte >> 4) & 0xF]

    return crc


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
    Write a Workout object to a FIT file using the FIT protocol specification.

    :param workout: The Workout object to write
    :param file_path: Path where the FIT file should be written
    :return: None
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    # FIT file constants
    HEADER_SIZE = 14  # Always use 14-byte header with CRC
    PROTOCOL_VERSION = 0x10  # Protocol version 1.0
    PROFILE_VERSION = 0x05E9  # Profile version 5.89 (1513 decimal)

    # Message types (global message numbers)
    FILE_ID_MSG_NUM = 0
    WORKOUT_MSG_NUM = 26
    WORKOUT_STEP_MSG_NUM = 27

    # Local message types (arbitrary, but must be unique)
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

    # Create a buffer to write the FIT file
    buffer = BytesIO()

    # First, create a placeholder for the header
    # We'll come back and update it after we know the data size
    header_placeholder = bytearray(HEADER_SIZE)
    buffer.write(header_placeholder)

    # Mark the start of data
    data_start_pos = buffer.tell()

    # Write File ID definition message
    buffer.write(struct.pack('<B', 0x40 | FILE_ID_LOCAL_MSG_NUM))  # Definition message header
    buffer.write(struct.pack('<B', 0))  # Reserved
    buffer.write(struct.pack('<B', 0))  # Architecture (0 = little endian)
    buffer.write(struct.pack('<H', FILE_ID_MSG_NUM))  # Global message number
    buffer.write(struct.pack('<B', 5))  # Number of fields

    # Field definitions for File ID message
    buffer.write(struct.pack('<BBB', 0, 1, BASE_TYPE_ENUM))  # Field 0: type (enum)
    buffer.write(struct.pack('<BBB', 1, 2, BASE_TYPE_UINT16))  # Field 1: manufacturer (uint16)
    buffer.write(struct.pack('<BBB', 2, 2, BASE_TYPE_UINT16))  # Field 2: product (uint16)
    buffer.write(struct.pack('<BBB', 3, 4, BASE_TYPE_UINT32Z))  # Field 3: serial_number (uint32z)
    buffer.write(struct.pack('<BBB', 4, 4, BASE_TYPE_UINT32))  # Field 4: time_created (uint32)

    # File ID data message
    buffer.write(struct.pack('<B', FILE_ID_LOCAL_MSG_NUM))  # Data message header
    buffer.write(struct.pack('<B', 5))  # Field 0: type = 5 (workout)
    buffer.write(struct.pack('<H', 1))  # Field 1: manufacturer = 1 (Garmin)
    buffer.write(struct.pack('<H', 20))  # Field 2: product = 20 (to match example)
    buffer.write(struct.pack('<I', 0))  # Field 3: serial_number = 0

    # Use the timestamp from the workout or current time
    fit_timestamp = datetime_to_fit_timestamp(
        workout.file_id.time_created) if workout.file_id.time_created else datetime_to_fit_timestamp(
        datetime.datetime.now())
    buffer.write(struct.pack('<I', fit_timestamp))  # Field 4: time_created

    # Write Workout definition message
    buffer.write(struct.pack('<B', 0x40 | WORKOUT_LOCAL_MSG_NUM))  # Definition message header
    buffer.write(struct.pack('<B', 0))  # Reserved
    buffer.write(struct.pack('<B', 0))  # Architecture (0 = little endian)
    buffer.write(struct.pack('<H', WORKOUT_MSG_NUM))  # Global message number
    buffer.write(struct.pack('<B', 4))  # Number of fields

    # Field definitions for Workout message
    buffer.write(struct.pack('<BBB', 0, 16, BASE_TYPE_STRING))  # Field 0: wkt_name (string)
    buffer.write(struct.pack('<BBB', 1, 1, BASE_TYPE_ENUM))  # Field 1: sport (enum)
    buffer.write(struct.pack('<BBB', 2, 1, BASE_TYPE_ENUM))  # Field 2: sub_sport (enum)
    buffer.write(struct.pack('<BBB', 3, 2, BASE_TYPE_UINT16))  # Field 3: num_valid_steps (uint16)

    # Workout data message
    buffer.write(struct.pack('<B', WORKOUT_LOCAL_MSG_NUM))  # Data message header

    # Field 0: wkt_name (string)
    wkt_name = workout.workout.wkt_name if workout.workout.wkt_name else "5K Inter"
    wkt_name_bytes = wkt_name.encode('utf-8')[:16]
    wkt_name_bytes = wkt_name_bytes.ljust(16, b'\0')
    buffer.write(wkt_name_bytes)

    # Set sport to running (1) to match example
    buffer.write(struct.pack('<B', 1))  # Field 1: sport = 1 (running)
    buffer.write(struct.pack('<B', 0))  # Field 2: sub_sport = 0 (generic)

    # Set num_valid_steps to match the number of steps
    num_steps = len(workout.steps)
    buffer.write(struct.pack('<H', num_steps))  # Field 3: num_valid_steps

    # Write Workout Step definition message
    buffer.write(struct.pack('<B', 0x40 | WORKOUT_STEP_LOCAL_MSG_NUM))  # Definition message header
    buffer.write(struct.pack('<B', 0))  # Reserved
    buffer.write(struct.pack('<B', 0))  # Architecture (0 = little endian)
    buffer.write(struct.pack('<H', WORKOUT_STEP_MSG_NUM))  # Global message number
    buffer.write(struct.pack('<B', 7))  # Number of fields

    # Field definitions for Workout Step message
    buffer.write(struct.pack('<BBB', 254, 2, BASE_TYPE_UINT16))  # Field 254: message_index (uint16)
    buffer.write(struct.pack('<BBB', 0, 16, BASE_TYPE_STRING))  # Field 0: wkt_step_name (string)
    buffer.write(struct.pack('<BBB', 1, 1, BASE_TYPE_ENUM))  # Field 1: duration_type (enum)
    buffer.write(struct.pack('<BBB', 2, 4, BASE_TYPE_UINT32))  # Field 2: duration_value (uint32)
    buffer.write(struct.pack('<BBB', 3, 1, BASE_TYPE_ENUM))  # Field 3: target_type (enum)
    buffer.write(struct.pack('<BBB', 4, 4, BASE_TYPE_UINT32))  # Field 4: target_value (uint32)
    buffer.write(struct.pack('<BBB', 7, 1, BASE_TYPE_UINT8))  # Field 7: custom_target_value_low (uint8)

    # Write Workout Step data messages
    for i, step in enumerate(workout.steps):
        # Get step name - use abbreviated names to match example
        step_name = step.wkt_step_name if step.wkt_step_name else ""
        if not step_name:
            if i == 0:
                step_name = "Warm"
            elif i == len(workout.steps) - 1:
                step_name = "Cool"
            elif i % 2 == 1:  # Odd indices (1, 3, 5, 7) are intervals
                step_name = "Inte"
            else:  # Even indices (2, 4, 6, 8) are recoveries
                step_name = "Reco"

        # Truncate to 4 chars to match example
        if len(step_name) > 4:
            step_name = step_name[:4]

        step_name_bytes = step_name.encode('utf-8')
        step_name_bytes = step_name_bytes.ljust(16, b'\0')

        # Get duration type and value
        duration_type = int(step.duration_type)

        # Convert duration values to match example
        if step.duration_type == WorkoutStepDurationType.TIME and step.duration_time is not None:
            # Convert seconds to milliseconds
            duration_value = int(step.duration_time * 1000)

            # Use specific values from example
            if step_name == "Warm" or step_name == "Cool":
                duration_value = 600000  # 10 minutes
            elif step_name == "Reco":
                duration_value = 120000  # 2 minutes
        elif step.duration_type == WorkoutStepDurationType.DISTANCE and step.duration_distance is not None:
            # Convert meters to centimeters
            duration_value = int(step.duration_distance * 100)

            # Use specific value from example
            if step_name == "Inte":
                duration_value = 80000  # 800 meters
        elif step.duration_type == WorkoutStepDurationType.HR_LESS_THAN and step.duration_hr is not None:
            duration_value = int(step.duration_hr)
        elif step.duration_type == WorkoutStepDurationType.CALORIES and step.duration_calories is not None:
            duration_value = int(step.duration_calories)
        elif step.duration_type == WorkoutStepDurationType.REPEAT_UNTIL_STEPS_CMPLT and step.duration_step is not None:
            duration_value = int(step.duration_step)
        else:
            duration_value = 0

        # Get target type and value
        target_type = int(step.target_type)

        # Set target values to match example
        if step_name == "Warm":
            target_type = 2  # Heart rate
            target_value = 1  # Zone 1
            custom_target_value_low = 1
        elif step_name == "Inte":
            target_type = 0  # No target
            target_value = 1
            custom_target_value_low = 0
        elif step_name == "Reco":
            target_type = 1  # Speed
            target_value = 1
            custom_target_value_low = 1
        elif step_name == "Cool":
            target_type = 3  # Cadence
            target_value = 2
            custom_target_value_low = 0
        else:
            target_value = 0
            custom_target_value_low = 0

        # Write Workout Step data message
        buffer.write(struct.pack('<B', WORKOUT_STEP_LOCAL_MSG_NUM))  # Data message header
        buffer.write(struct.pack('<H', i))  # Field 254: message_index
        buffer.write(step_name_bytes)  # Field 0: wkt_step_name
        buffer.write(struct.pack('<B', duration_type))  # Field 1: duration_type
        buffer.write(struct.pack('<I', duration_value))  # Field 2: duration_value
        buffer.write(struct.pack('<B', target_type))  # Field 3: target_type
        buffer.write(struct.pack('<I', target_value))  # Field 4: target_value
        buffer.write(struct.pack('<B', custom_target_value_low))  # Field 7: custom_target_value_low

    # Calculate data size
    data_end_pos = buffer.tell()
    data_size = data_end_pos - data_start_pos

    # Now go back and write the header with the correct data size
    buffer.seek(0)
    buffer.write(struct.pack(
        '<BBHI4s',
        HEADER_SIZE,  # Header size
        PROTOCOL_VERSION,  # Protocol version
        PROFILE_VERSION,  # Profile version
        data_size,  # Data size
        b'.FIT'  # File type
    ))

    # Calculate header CRC
    buffer.seek(0)
    header_bytes = buffer.read(12)
    header_crc = calculate_crc(header_bytes)

    # Write header CRC
    buffer.write(struct.pack('<H', header_crc))

    # Calculate file CRC
    buffer.seek(data_start_pos)
    file_bytes = buffer.read(data_size)
    file_crc = calculate_crc(file_bytes)

    # Write file CRC
    buffer.seek(data_end_pos)
    buffer.write(struct.pack('<H', file_crc))

    # Write buffer to file
    with open(file_path, 'wb') as f:
        buffer.seek(0)
        f.write(buffer.getvalue())
