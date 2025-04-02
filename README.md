# FIT Workout Library

A Python library for working with Garmin FIT workout files using Pydantic models.

## Overview

This library provides a structured way to create, read, and write FIT workout files using Pydantic models. It allows you to:

- Read existing FIT workout files into Pydantic models
- Create workout definitions programmatically using Pydantic models
- Write workout definitions to FIT files

The library supports various workout types including running, cycling, and strength training, and handles different workout step types, target types, and custom target values.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fitlib.git

# Install dependencies
cd fitlib
pip install -r requirements.txt
```

## Dependencies

- Python 3.6+
- pydantic
- fitparse
- fitdecode (optional, for advanced FIT file writing)

## Usage

### Reading a FIT Workout File

```python
from fitlib.converter import read_fit_file

# Read a FIT workout file
workout = read_fit_file("path/to/workout.fit")

# Access workout properties
print(f"Workout Name: {workout.workout.wkt_name}")
print(f"Sport: {workout.workout.sport}")
print(f"Number of Steps: {len(workout.steps)}")

# Access step properties
for i, step in enumerate(workout.steps):
    print(f"Step {i+1}: {step.wkt_step_name}")
    print(f"  Duration Type: {step.duration_type}")
    print(f"  Target Type: {step.target_type}")
```

### Creating a Workout Definition

```python
from datetime import datetime
from fitlib.models import (
    FileType, Sport, SubSport, Intensity,
    WorkoutStepDurationType, WorkoutStepTargetType,
    FileIdMessage, WorkoutMessage, WorkoutStep, Workout
)

# Create file ID message
file_id = FileIdMessage(
    type=FileType.WORKOUT,
    manufacturer=1,  # Garmin
    product=20,
    time_created=datetime.now()
)

# Create workout message
workout_msg = WorkoutMessage(
    wkt_name="My Workout",
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
        custom_target_heart_rate_low=150,
        custom_target_heart_rate_high=160
    ),
    
    # Cool-down step
    WorkoutStep(
        message_index=2,
        wkt_step_name="Cool Down",
        intensity=Intensity.COOLDOWN,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=600.0,  # 10 minutes
        target_type=WorkoutStepTargetType.OPEN
    )
]

# Create the complete workout
my_workout = Workout(
    file_id=file_id,
    workout=workout_msg,
    steps=steps
)
```

### Writing a Workout to a FIT File

```python
from fitlib.converter import write_fit_file

# Write the workout to a FIT file
write_fit_file(my_workout, "path/to/output.fit")
```

## Examples

The library includes several example workout definitions:

- Running interval workout
- Cycling power workout
- Strength training workout
- Workout with repeat steps

You can find these examples in the `examples.py` file.

```python
from fitlib.examples import (
    create_running_interval_workout,
    create_cycling_power_workout,
    create_strength_workout,
    create_workout_with_repeats
)

# Create a running interval workout
running_workout = create_running_interval_workout()

# Write it to a FIT file
write_fit_file(running_workout, "running_workout.fit")
```

## Capabilities and Limitations

### Capabilities

1. Reading FIT workout files into Pydantic models
2. Creating workout definitions using Pydantic models
3. Support for various workout types (running, cycling, strength)
4. Support for different step types (time, distance, heart rate, etc.)
5. Support for different target types (heart rate, power, cadence, etc.)
6. Support for custom target values (heart rate ranges, power ranges, etc.)
7. Support for repeat steps

### Limitations

1. Writing FIT files has some format issues - files can be created but may not be readable by all devices
2. Limited validation of workout parameters beyond Pydantic's type checking
3. No support for advanced features like workout equipment or workout categories
4. No GUI for creating workouts (command-line interface only)

## Future Improvements

1. Improve FIT file writing to ensure compatibility with all devices
2. Add more validation for workout parameters
3. Support for more advanced workout features
4. Create a simple GUI for creating workouts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Garmin for the FIT file format documentation
- The fitparse and fitdecode libraries for FIT file parsing
- Pydantic for the data validation and settings management
