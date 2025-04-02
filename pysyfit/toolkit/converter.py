import logging
import os
import struct

from fitparse import FitFile

from pysyfit.models.enum_types import FileType, SubSport, Sport, WorkoutStepDurationType, WorkoutStepTargetType, \
    Intensity
from pysyfit.models.workout_models import Workout, FileIdMessage, WorkoutMessage, WorkoutStep
from pysyfit.utils.timestamp_utils import fit_timestamp_to_datetime, datetime_to_fit_timestamp


def read_fit_file(file_path: str) -> Workout:
    """
    Read a FIT file and convert it to a Workout object.
    :param file_path: Path to the FIT file
    :return: Workout object containing the parsed data
    """
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

    logging.info("Process file ID message")
    file_id = FileIdMessage(
        type=file_type,
        manufacturer=manufacturer,
        product=file_id_data.get('product', 0),
        serial_number=file_id_data.get('serial_number'),
        time_created=fit_timestamp_to_datetime(file_id_data.get('time_created', 0)),
        number=file_id_data.get('number')
    )
    
    logging.info("Process workout message")
    workout_data = workout_msgs[0].get_values()
    workout = WorkoutMessage(
        wkt_name=workout_data.get('wkt_name', ''),
        sport=Sport(workout_data.get('sport', Sport.GENERIC)),
        sub_sport=SubSport(workout_data.get('sub_sport', SubSport.GENERIC)),
        num_valid_steps=workout_data.get('num_valid_steps', len(workout_step_msgs))
    )
    
    logging.info("Process workout step messages")
    steps = []
    for step_msg in workout_step_msgs:
        step_data = step_msg.get_values()
        
        logging.info("Extract duration-related fields")
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
        
        logging.info("Extract target-related fields")
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
            
        logging.info("Create workout step")
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
    
    logging.info("Rreturning the complete workout")
    return Workout(
        file_id=file_id,
        workout=workout,
        steps=steps
    )


def write_fit_file(workout: Workout, file_path: str) -> None:
    """
    Write a Workout object to a FIT file.
    :param workout: The Workout object to write
    :param file_path: Path where the FIT file should be written
    :return: None
    """

    logging.info("Creating directory for output file if it doesn't exist")
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    logging.info("Defining FIT file header")
    header_size = 14
    protocol_version = 16
    profile_version = 1320
    data_size = 0
    data_type = b'.FIT'
    crc = 0
    
    file_id_msg_def = struct.pack('<BBHB', 0, 0, 0, 5)
    file_id_msg_fields = struct.pack('<BBBBB', 0, 1, 0, 1, 0)
    
    logging.info("Creating FIT file")
    file_id_msg_data = struct.pack('<BBBBI', 
                                  0,  # Normal header
                                  0,  # Message number (File ID)
                                  int(workout.file_id.type),  # Type (5 = workout)
                                  workout.file_id.manufacturer,  # Manufacturer
                                  int(datetime_to_fit_timestamp(workout.file_id.time_created)))  # Time created

    workout_msg_def = struct.pack('<BBHB', 0, 19, 0, 3)  # Message definition for Workout
    workout_msg_fields = struct.pack('<BBBBBB', 8, 16, 0, 0, 1, 0)  # Field definitions
    workout_name = workout.workout.wkt_name.encode('utf-8')
    workout_name = workout_name[:16].ljust(16, b'\0')  # Ensure 16 bytes, pad with nulls
    workout_msg_data = struct.pack('<BB16sBB', 
                                  0,  # Normal header
                                  19,  # Message number (Workout)
                                  workout_name,  # Workout name
                                  int(workout.workout.sport),  # Sport
                                  len(workout.steps))  # Number of valid steps

    logging.info("Writing steps")
    workout_step_msgs = []
    for step in workout.steps:
        workout_step_msg_def = struct.pack('<BBHB', 0, 20, 0, 4)  # 4 fields instead of 5
        workout_step_msg_fields = struct.pack('<BBBBBBBBB',
                                             254, 2, 0,  # message_index (3 items)
                                             1, 1, 0,    # duration_type (3 items)
                                             2, 4, 0)    # duration_value (3 items)
        
        step_name = b''
        if step.wkt_step_name:
            step_name = step.wkt_step_name.encode('utf-8')[:16].ljust(16, b'\0')
        else:
            step_name = b'Step'.ljust(16, b'\0')
        
        workout_step_msg_data = struct.pack('<BBH',
                                           0,  # Normal header
                                           20,  # Message number (Workout Step)
                                           step.message_index)  # Message index
        
        workout_step_msg_data += struct.pack('<B',
                                           int(step.duration_type))  # Duration type
        workout_step_msg_data += struct.pack('<f',
                                           step.duration_value if step.duration_value is not None else 0.0)  # Duration value
        workout_step_msg_data += struct.pack('<B',
                                           int(step.intensity))
        
        workout_step_msgs.append((workout_step_msg_def, workout_step_msg_fields, workout_step_msg_data))
    
    data_size = (len(file_id_msg_def) + len(file_id_msg_fields) + len(file_id_msg_data) +
                len(workout_msg_def) + len(workout_msg_fields) + len(workout_msg_data))
    
    for msg_def, msg_fields, msg_data in workout_step_msgs:
        data_size += len(msg_def) + len(msg_fields) + len(msg_data)
    
    logging.info("Writing file...")
    with open(file_path, 'wb') as f:
        f.write(
            struct.pack(
                '<BBHI4sH',
                header_size,
                protocol_version,
                profile_version,
                data_size,
                data_type,
                crc,
            )
        )
        
        f.write(file_id_msg_def)
        f.write(file_id_msg_fields)
        f.write(file_id_msg_data)
        f.write(workout_msg_def)
        f.write(workout_msg_fields)
        f.write(workout_msg_data)
        
        for msg_def, msg_fields, msg_data in workout_step_msgs:
            f.write(msg_def)
            f.write(msg_fields)
            f.write(msg_data)
        
        f.write(struct.pack('<H', 0))
    logging.info(f"FIT file written successfully to {file_path}")
    print(f"Successfully wrote FIT file to {file_path}")
