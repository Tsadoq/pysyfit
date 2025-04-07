"""
Example workout definitions using the FIT workout library.

This module demonstrates how to create workout definitions using the Pydantic models
and how to convert them to FIT files.
"""

from datetime import datetime

from pysyfit.models.enum_types import SubSport, Sport
from pysyfit.models.workout_models import (
    FileType, Intensity,
    WorkoutStepDurationType, WorkoutStepTargetType,
    FileIdMessage, WorkoutMessage, WorkoutStep, Workout
)
from pysyfit.toolkit.converter import write_fit_file


def create_running_interval_workout():
    """
    Create a running interval workout with warm-up, intervals, and cool-down.
    
    Returns:
        Workout: A running interval workout
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
        wkt_name="5K Interval Training",
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
            duration_time=600.0,  # 10 minutes
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),
        
        # Interval 1
        WorkoutStep(
            message_index=1,
            wkt_step_name="Interval 1",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=800.0,  # 800 meters
            target_type=WorkoutStepTargetType.HEART_RATE,
            custom_target_heart_rate_low=160,
            custom_target_heart_rate_high=170
        ),
        
        # Recovery 1
        WorkoutStep(
            message_index=2,
            wkt_step_name="Recovery 1",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),
        
        # Interval 2
        WorkoutStep(
            message_index=3,
            wkt_step_name="Interval 2",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=800.0,  # 800 meters
            target_type=WorkoutStepTargetType.HEART_RATE,
            custom_target_heart_rate_low=160,
            custom_target_heart_rate_high=170
        ),
        
        # Recovery 2
        WorkoutStep(
            message_index=4,
            wkt_step_name="Recovery 2",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),
        
        # Interval 3
        WorkoutStep(
            message_index=5,
            wkt_step_name="Interval 3",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=800.0,  # 800 meters
            target_type=WorkoutStepTargetType.HEART_RATE,
            custom_target_heart_rate_low=160,
            custom_target_heart_rate_high=170
        ),
        
        # Recovery 3
        WorkoutStep(
            message_index=6,
            wkt_step_name="Recovery 3",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),
        
        # Interval 4
        WorkoutStep(
            message_index=7,
            wkt_step_name="Interval 4",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=800.0,  # 800 meters
            target_type=WorkoutStepTargetType.HEART_RATE,
            custom_target_heart_rate_low=160,
            custom_target_heart_rate_high=170
        ),
        
        # Recovery 4
        WorkoutStep(
            message_index=8,
            wkt_step_name="Recovery 4",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),
        
        # Cool-down step
        WorkoutStep(
            message_index=9,
            wkt_step_name="Cool Down",
            intensity=Intensity.COOLDOWN,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=600.0,  # 10 minutes
            target_type=WorkoutStepTargetType.OPEN
        )
    ]
    
    # Create and return the complete workout
    return Workout(
        file_id=file_id,
        workout=workout,
        steps=steps
    )


def create_cycling_power_workout():
    """
    Create a cycling power-based workout with warm-up, intervals, and cool-down.
    
    Returns:
        Workout: A cycling power-based workout
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
        wkt_name="Power Intervals",
        sport=Sport.CYCLING,
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
            duration_time=900.0,  # 15 minutes
            target_type=WorkoutStepTargetType.POWER,
            target_power_zone=1
        ),
        
        # Interval 1
        WorkoutStep(
            message_index=1,
            wkt_step_name="Power Interval 1",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=180.0,  # 3 minutes
            target_type=WorkoutStepTargetType.POWER,
            custom_target_power_low=250,
            custom_target_power_high=270
        ),
        
        # Recovery 1
        WorkoutStep(
            message_index=2,
            wkt_step_name="Recovery 1",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.POWER,
            custom_target_power_low=120,
            custom_target_power_high=140
        ),
        
        # Interval 2
        WorkoutStep(
            message_index=3,
            wkt_step_name="Power Interval 2",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=180.0,  # 3 minutes
            target_type=WorkoutStepTargetType.POWER,
            custom_target_power_low=250,
            custom_target_power_high=270
        ),
        
        # Recovery 2
        WorkoutStep(
            message_index=4,
            wkt_step_name="Recovery 2",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.POWER,
            custom_target_power_low=120,
            custom_target_power_high=140
        ),
        
        # Interval 3
        WorkoutStep(
            message_index=5,
            wkt_step_name="Power Interval 3",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=180.0,  # 3 minutes
            target_type=WorkoutStepTargetType.POWER,
            custom_target_power_low=250,
            custom_target_power_high=270
        ),
        
        # Recovery 3
        WorkoutStep(
            message_index=6,
            wkt_step_name="Recovery 3",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.POWER,
            custom_target_power_low=120,
            custom_target_power_high=140
        ),
        
        # Interval 4
        WorkoutStep(
            message_index=7,
            wkt_step_name="Power Interval 4",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=180.0,  # 3 minutes
            target_type=WorkoutStepTargetType.POWER,
            custom_target_power_low=250,
            custom_target_power_high=270
        ),
        
        # Recovery 4
        WorkoutStep(
            message_index=8,
            wkt_step_name="Recovery 4",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=120.0,  # 2 minutes
            target_type=WorkoutStepTargetType.POWER,
            custom_target_power_low=120,
            custom_target_power_high=140
        ),
        
        # Cool-down step
        WorkoutStep(
            message_index=9,
            wkt_step_name="Cool Down",
            intensity=Intensity.COOLDOWN,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=600.0,  # 10 minutes
            target_type=WorkoutStepTargetType.POWER,
            target_power_zone=1
        )
    ]
    
    # Create and return the complete workout
    return Workout(
        file_id=file_id,
        workout=workout,
        steps=steps
    )


def create_strength_workout():
    """
    Create a strength training workout with multiple exercises.
    
    Returns:
        Workout: A strength training workout
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
        wkt_name="Full Body Strength",
        sport=Sport.TRAINING,
        sub_sport=SubSport.STRENGTH_TRAINING
    )
    
    # Create workout steps
    steps = [
        # Warm-up
        WorkoutStep(
            message_index=0,
            wkt_step_name="Warm Up",
            intensity=Intensity.WARMUP,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=300.0,  # 5 minutes
            target_type=WorkoutStepTargetType.OPEN
        ),
        
        # Exercise 1: Squats
        WorkoutStep(
            message_index=1,
            wkt_step_name="Squats",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.REPETITION_TIME,
            duration_time=60.0,  # 1 minute
            target_type=WorkoutStepTargetType.OPEN,
            notes="3 sets of 12 reps"
        ),
        
        # Rest after Exercise 1
        WorkoutStep(
            message_index=2,
            wkt_step_name="Rest",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=60.0,  # 1 minute
            target_type=WorkoutStepTargetType.OPEN
        ),
        
        # Exercise 2: Push-ups
        WorkoutStep(
            message_index=3,
            wkt_step_name="Push-ups",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.REPETITION_TIME,
            duration_time=60.0,  # 1 minute
            target_type=WorkoutStepTargetType.OPEN,
            notes="3 sets of 10 reps"
        ),
        
        # Rest after Exercise 2
        WorkoutStep(
            message_index=4,
            wkt_step_name="Rest",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=60.0,  # 1 minute
            target_type=WorkoutStepTargetType.OPEN
        ),
        
        # Exercise 3: Lunges
        WorkoutStep(
            message_index=5,
            wkt_step_name="Lunges",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.REPETITION_TIME,
            duration_time=60.0,  # 1 minute
            target_type=WorkoutStepTargetType.OPEN,
            notes="3 sets of 10 reps each leg"
        ),
        
        # Rest after Exercise 3
        WorkoutStep(
            message_index=6,
            wkt_step_name="Rest",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=60.0,  # 1 minute
            target_type=WorkoutStepTargetType.OPEN
        ),
        
        # Exercise 4: Plank
        WorkoutStep(
            message_index=7,
            wkt_step_name="Plank",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=30.0,  # 30 seconds
            target_type=WorkoutStepTargetType.OPEN,
            notes="3 sets of 30 seconds"
        ),
        
        # Rest after Exercise 4
        WorkoutStep(
            message_index=8,
            wkt_step_name="Rest",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=60.0,  # 1 minute
            target_type=WorkoutStepTargetType.OPEN
        ),
        
        # Cool-down
        WorkoutStep(
            message_index=9,
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


def create_workout_with_repeats():
    """
    Create a workout with repeat steps.
    
    Returns:
        Workout: A workout with repeat steps
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
        wkt_name="Repeat Workout",
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
            duration_time=600.0,  # 10 minutes
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),
        
        # Interval step
        WorkoutStep(
            message_index=1,
            wkt_step_name="Interval",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.DISTANCE,
            duration_distance=400.0,  # 400 meters
            target_type=WorkoutStepTargetType.HEART_RATE,
            custom_target_heart_rate_low=160,
            custom_target_heart_rate_high=170
        ),
        
        # Recovery step
        WorkoutStep(
            message_index=2,
            wkt_step_name="Recovery",
            intensity=Intensity.REST,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=60.0,  # 1 minute
            target_type=WorkoutStepTargetType.HEART_RATE,
            target_hr_zone=1
        ),
        
        # Repeat step - repeat the previous 2 steps 5 times
        WorkoutStep(
            message_index=3,
            wkt_step_name="Repeat",
            intensity=Intensity.ACTIVE,
            duration_type=WorkoutStepDurationType.REPEAT_UNTIL_STEPS_CMPLT,
            duration_step=5,  # Repeat 5 times
            target_type=WorkoutStepTargetType.OPEN
        ),
        
        # Cool-down step
        WorkoutStep(
            message_index=4,
            wkt_step_name="Cool Down",
            intensity=Intensity.COOLDOWN,
            duration_type=WorkoutStepDurationType.TIME,
            duration_time=600.0,  # 10 minutes
            target_type=WorkoutStepTargetType.OPEN
        )
    ]
    
    # Create and return the complete workout
    return Workout(
        file_id=file_id,
        workout=workout,
        steps=steps
    )


if __name__ == "__main__":
    # Create output directory
    import os
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and save running interval workout
    running_workout = create_running_interval_workout()
    running_output_path = os.path.join(output_dir, "running_interval_workout.fit")
    write_fit_file(running_workout, running_output_path)
    print(f"Created running interval workout: {running_output_path}")
    
    # Create and save cycling power workout
    cycling_workout = create_cycling_power_workout()
    cycling_output_path = os.path.join(output_dir, "cycling_power_workout.fit")
    write_fit_file(cycling_workout, cycling_output_path)
    print(f"Created cycling power workout: {cycling_output_path}")
    
    # Create and save strength workout
    strength_workout = create_strength_workout()
    strength_output_path = os.path.join(output_dir, "strength_workout.fit")
    write_fit_file(strength_workout, strength_output_path)
    print(f"Created strength workout: {strength_output_path}")
    
    # Create and save workout with repeats
    repeat_workout = create_workout_with_repeats()
    repeat_output_path = os.path.join(output_dir, "repeat_workout.fit")
    write_fit_file(repeat_workout, repeat_output_path)
    print(f"Created workout with repeats: {repeat_output_path}")
