"""
Test module for FIT workout file conversion.

This module tests the conversion between Pydantic models and FIT files.
"""

import os
import tempfile
from datetime import datetime

from pysyfit.models.enum_types import SubSport, Sport
from pysyfit.models.workout_models import (
    FileType, Intensity,
    WorkoutStepDurationType, WorkoutStepTargetType,
    FileIdMessage, WorkoutMessage, WorkoutStep, Workout
)
from pysyfit.toolkit.converter import read_fit_file, write_fit_file


def test_read_fit_file(fit_file_path):
    """
    Test reading a FIT file and converting it to a Workout object.
    
    Args:
        fit_file_path: Path to the FIT file to test
    
    Returns:
        Workout: The parsed Workout object
    """
    print(f"Testing read_fit_file with {fit_file_path}")
    
    try:
        workout = read_fit_file(fit_file_path)
        
        # Print workout details
        print(f"Workout Name: {workout.workout.wkt_name}")
        print(f"Sport: {Sport(workout.workout.sport).name}")
        print(f"Sub Sport: {SubSport(workout.workout.sub_sport).name}")
        print(f"Number of Steps: {len(workout.steps)}")
        
        # Print details of each step
        for i, step in enumerate(workout.steps):
            print(f"\nStep {i+1}:")
            print(f"  Name: {step.wkt_step_name}")
            print(f"  Intensity: {Intensity(step.intensity).name}")
            print(f"  Duration Type: {WorkoutStepDurationType(step.duration_type).name}")
            
            # Print duration value based on duration type
            if step.duration_type == WorkoutStepDurationType.TIME:
                print(f"  Duration: {step.duration_time} seconds")
            elif step.duration_type == WorkoutStepDurationType.DISTANCE:
                print(f"  Duration: {step.duration_distance} meters")
            elif step.duration_type in [WorkoutStepDurationType.HR_LESS_THAN, WorkoutStepDurationType.HR_GREATER_THAN]:
                print(f"  Duration: Heart Rate {step.duration_hr} bpm")
            elif step.duration_type == WorkoutStepDurationType.CALORIES:
                print(f"  Duration: {step.duration_calories} calories")
            elif step.duration_type in [WorkoutStepDurationType.REPEAT_UNTIL_STEPS_CMPLT]:
                print(f"  Duration: Repeat {step.duration_step} steps")
            elif step.duration_type == WorkoutStepDurationType.OPEN:
                print(f"  Duration: Open (until lap button)")
            
            # Print target type and value
            print(f"  Target Type: {WorkoutStepTargetType(step.target_type).name}")
            
            if step.target_type == WorkoutStepTargetType.HEART_RATE:
                if step.target_hr_zone is not None:
                    print(f"  Target: Heart Rate Zone {step.target_hr_zone}")
                if step.custom_target_heart_rate_low is not None and step.custom_target_heart_rate_high is not None:
                    print(f"  Custom Target: {step.custom_target_heart_rate_low}-{step.custom_target_heart_rate_high} bpm")
            elif step.target_type == WorkoutStepTargetType.POWER:
                if step.target_power_zone is not None:
                    print(f"  Target: Power Zone {step.target_power_zone}")
                if step.custom_target_power_low is not None and step.custom_target_power_high is not None:
                    print(f"  Custom Target: {step.custom_target_power_low}-{step.custom_target_power_high} watts")
            elif step.target_type == WorkoutStepTargetType.CADENCE:
                if step.target_cadence_zone is not None:
                    print(f"  Target: Cadence Zone {step.target_cadence_zone}")
                if step.custom_target_cadence_low is not None and step.custom_target_cadence_high is not None:
                    print(f"  Custom Target: {step.custom_target_cadence_low}-{step.custom_target_cadence_high} rpm")
            elif step.target_type == WorkoutStepTargetType.SPEED:
                if step.target_speed_zone is not None:
                    print(f"  Target: Speed Zone {step.target_speed_zone}")
                if step.custom_target_speed_low is not None and step.custom_target_speed_high is not None:
                    print(f"  Custom Target: {step.custom_target_speed_low}-{step.custom_target_speed_high} m/s")
            elif step.target_type == WorkoutStepTargetType.OPEN:
                print(f"  Target: Open (no specific target)")
        
        return workout
    
    except Exception as e:
        print(f"Error reading FIT file: {e}")
        return None


def test_write_fit_file(workout, output_path):
    """
    Test writing a Workout object to a FIT file.
    
    Args:
        workout: The Workout object to write
        output_path: Path where the FIT file should be written
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Testing write_fit_file to {output_path}")
    
    try:
        write_fit_file(workout, output_path)
        print(f"Successfully wrote FIT file to {output_path}")
        return True
    
    except Exception as e:
        print(f"Error writing FIT file: {e}")
        return False


def test_roundtrip(fit_file_path, output_dir=None):
    """
    Test reading a FIT file, converting it to a Workout object,
    then writing it back to a new FIT file.
    
    Args:
        fit_file_path: Path to the input FIT file
        output_dir: Directory where the output FIT file should be written
                   (if None, a temporary directory will be used)
    
    Returns:
        tuple: (success, input_workout, output_workout, output_path)
    """
    print(f"Testing roundtrip conversion with {fit_file_path}")
    
    # Read the input FIT file
    input_workout = read_fit_file(fit_file_path)
    if input_workout is None:
        return False, None, None, None
    
    # Create output path
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    
    base_name = os.path.basename(fit_file_path)
    output_path = os.path.join(output_dir, f"output_{base_name}")
    
    # Write the workout to a new FIT file
    success = test_write_fit_file(input_workout, output_path)
    if not success:
        return False, input_workout, None, output_path
    
    # Read the output FIT file
    output_workout = read_fit_file(output_path)
    if output_workout is None:
        return False, input_workout, None, output_path
    
    print("\nComparison of input and output workouts:")
    print(f"Input workout name: {input_workout.workout.wkt_name}")
    print(f"Output workout name: {output_workout.workout.wkt_name}")
    print(f"Input steps: {len(input_workout.steps)}")
    print(f"Output steps: {len(output_workout.steps)}")
    
    return True, input_workout, output_workout, output_path


def create_sample_workout():
    """
    Create a sample workout for testing.
    
    Returns:
        Workout: A sample workout
    """
    # Create file ID message
    file_id = FileIdMessage(
        type=FileType.WORKOUT,
        manufacturer=1,  # Garmin
        product=20,
        time_created=datetime.now()
    )
    
    # Create workout message
    workout = WorkoutMessage(
        wkt_name="Sample Workout",
        sport=Sport.RUNNING,
        sub_sport=SubSport.GENERIC
    )
    
    # Create workout steps
    steps = [
        # Warm-up step
        WorkoutStep(
            message_index=0,
            wkt_step_name="Warm Up",
            intensity=Intensity.WARMUP,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=300.0,  # 5 minutes
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),
        
        # Interval step 1
        WorkoutStep(
            message_index=1,
            wkt_step_name="Interval 1",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=400.0,  # 400 meters
            target_type=WorkoutStepTargetType.HEART_RATE,
            custom_target_heart_rate_low=150,
            custom_target_heart_rate_high=160
        ),
        
        # Recovery step 1
        WorkoutStep(
            message_index=2,
            wkt_step_name="Recovery 1",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=60.0,  # 1 minute
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),
        
        # Interval step 2
        WorkoutStep(
            message_index=3,
            wkt_step_name="Interval 2",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=400.0,  # 400 meters
            target_type=WorkoutStepTargetType.HEART_RATE,
            custom_target_heart_rate_low=150,
            custom_target_heart_rate_high=160
        ),
        
        # Recovery step 2
        WorkoutStep(
            message_index=4,
            wkt_step_name="Recovery 2",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=60.0,  # 1 minute
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),
        
        # Cool-down step
        WorkoutStep(
            message_index=5,
            wkt_step_name="Cool Down",
            intensity=Intensity.COOLDOWN,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=300.0,  # 5 minutes
            target_type=WorkoutStepTargetType.OPEN
        )
    ]
    
    # Create and return the complete workout
    return Workout(
        file_id=file_id,
        workout=workout,
        steps=steps
    )
