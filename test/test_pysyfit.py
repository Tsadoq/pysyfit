import os
import datetime

from pysyfit.models.enum_types import FileType, SubSport, Sport, WorkoutStepDurationType, WorkoutStepTargetType, \
    Intensity
from pysyfit.models.workout_models import Workout, FileIdMessage, WorkoutMessage, WorkoutStep
from pysyfit.toolkit.converter import write_fit_file


def create_test_workout():
    """Create a test workout with various step types"""
    # Create file ID message
    file_id = FileIdMessage(
        type=FileType.WORKOUT,
        manufacturer=1,  # Garmin
        product=20,
        serial_number=0,
        time_created=datetime.datetime.now(),
        number=None
    )

    # Create workout message
    workout = WorkoutMessage(
        wkt_name="5K Inter",
        sport=Sport.RUNNING,
        sub_sport=SubSport.GENERIC,
        num_valid_steps=10
    )

    # Create workout steps
    steps = [
        # Warm-up step
        WorkoutStep(
            message_index=0,
            wkt_step_name="Warm",
            intensity=Intensity.WARMUP,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=600.0,  # 10 minutes
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),

        # Interval 1
        WorkoutStep(
            message_index=1,
            wkt_step_name="Inte",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=800.0,  # 800 meters
            target_type=WorkoutStepTargetType.OPEN,
            target_value=1
        ),

        # Recovery 1
        WorkoutStep(
            message_index=2,
            wkt_step_name="Reco",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.SPEED,
            target_value=1
        ),

        # Interval 2
        WorkoutStep(
            message_index=3,
            wkt_step_name="Inte",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=800.0,  # 800 meters
            target_type=WorkoutStepTargetType.OPEN,
            target_value=1
        ),

        # Recovery 2
        WorkoutStep(
            message_index=4,
            wkt_step_name="Reco",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.SPEED,
            target_value=1
        ),

        # Interval 3
        WorkoutStep(
            message_index=5,
            wkt_step_name="Inte",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=800.0,  # 800 meters
            target_type=WorkoutStepTargetType.OPEN,
            target_value=1
        ),

        # Recovery 3
        WorkoutStep(
            message_index=6,
            wkt_step_name="Reco",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.SPEED,
            target_value=1
        ),

        # Interval 4
        WorkoutStep(
            message_index=7,
            wkt_step_name="Inte",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=800.0,  # 800 meters
            target_type=WorkoutStepTargetType.OPEN,
            target_value=1
        ),

        # Recovery 4
        WorkoutStep(
            message_index=8,
            wkt_step_name="Reco",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.SPEED,
            target_value=1
        ),

        # Cool-down step
        WorkoutStep(
            message_index=9,
            wkt_step_name="Cool",
            intensity=Intensity.COOLDOWN,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=600.0,  # 10 minutes
            target_type=WorkoutStepTargetType.CADENCE,
            target_value=2
        )
    ]

    # Create and return the complete workout
    return Workout(
        file_id=file_id,
        workout=workout,
        steps=steps
    )


def test_fit_file(fit_file_path):
    """Test if a FIT file can be read by the Garmin SDK without errors"""
    try:
        from fitparse import FitFile

        print(f"Testing file: {fit_file_path}")

        # Try to parse the file
        fit_file = FitFile(fit_file_path)
        fit_file.parse()

        # Check if the file has the expected messages
        file_id_msgs = list(fit_file.get_messages('file_id'))
        workout_msgs = list(fit_file.get_messages('workout'))
        workout_step_msgs = list(fit_file.get_messages('workout_step'))

        if not file_id_msgs:
            print("File integrity check failed: Missing file_id message")
            return False

        if not workout_msgs:
            print("File integrity check failed: Missing workout message")
            return False

        if not workout_step_msgs:
            print("File integrity check failed: Missing workout_step messages")
            return False

        # Print message details for debugging
        print("\nFile ID Message:")
        for field in file_id_msgs[0].fields:
            print(f"  {field.name}: {field.value}")

        print("\nWorkout Message:")
        for field in workout_msgs[0].fields:
            print(f"  {field.name}: {field.value}")

        print("\nWorkout Steps:")
        for i, step_msg in enumerate(workout_step_msgs):
            print(f"\nStep {i}:")
            for field in step_msg.fields:
                print(f"  {field.name}: {field.value}")

        print("\nFile integrity check passed")
        return True
    except Exception as e:
        print(f"File integrity check failed: {e}")
        return False


def hexdump(file_path):
    """Generate a hexdump of a file"""
    with open(file_path, 'rb') as f:
        data = f.read()

    print(f"Hexdump of {file_path}:")
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_values = ' '.join(f'{b:02x}' for b in chunk)
        printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"{i:04x}: {hex_values:<48}  {printable}")

    print(f"Total file size: {len(data)} bytes")


def main():
    # Create a test workout
    workout = create_test_workout()

    # Write the workout to a FIT file
    output_file = "./test/test_workout.fit"
    print(f"Writing workout to {output_file}")
    write_fit_file(workout, output_file)

    # Test the generated file
    test_result = test_fit_file(output_file)

    # Print hexdump for debugging
    hexdump(output_file)

    # Compare with sample file if available
    sample_file = "./test/WorkoutRepeatSteps.fit"
    if os.path.exists(sample_file):
        print("\nComparing with sample file:")
        hexdump(sample_file)

    # Print overall result
    if test_result:
        print("\nFile validity test: PASS")
        print("Overall test result: PASS")
    else:
        print("\nFile validity test: FAIL")
        print("Overall test result: FAIL")


if __name__ == "__main__":
    main()
