# PySyFit - Python Structured FIT Workout Library

A Python library for creating, reading, and manipulating structured workout files in the Garmin FIT format.

## Overview

PySyFit provides a structured, type-safe way to work with workout files in the FIT format. It uses Pydantic models to define the structure of workouts and provides tools to convert between these models and FIT files.

## Features

- Create structured workout definitions using Pydantic models
- Read existing FIT workout files into structured models
- Write workout models to valid FIT files
- Support for various workout types (running, cycling, strength training)
- Support for different workout step types (time, distance, repetitions, repeats)
- Support for different target types (heart rate, power, cadence)
- Support for custom target ranges

## Installation

```bash
pip install pysyfit
```

## Quick Start

### Creating a Workout

```python
from datetime import datetime
from pysyfit.models.enum_types import Sport, Intensity, WorkoutStepDurationType, WorkoutStepTargetType
from pysyfit.models.workout_models import Workout, FileIdMessage, WorkoutMessage, WorkoutStep
from pysyfit.toolkit.converter import write_fit_file

# Create File ID message
file_id = FileIdMessage(
    time_created=datetime.now()
)

# Create Workout message
workout_msg = WorkoutMessage(
    wkt_name="5K Interval Training",
    sport=Sport.RUNNING,
    num_valid_steps=4
)

# Create workout steps
steps = [
    # Warm-up step
    WorkoutStep(
        message_index=0,
        wkt_step_name="Warm Up",
        intensity=Intensity.WARMUP,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=600,  # 10 minutes in seconds
        target_type=WorkoutStepTargetType.HEART_RATE
    ),
    
    # Interval 1
    WorkoutStep(
        message_index=1,
        wkt_step_name="Interval 1",
        intensity=Intensity.ACTIVE,
        duration_type=WorkoutStepDurationType.DISTANCE,
        duration_distance=800,  # 800 meters
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
        duration_time=120,  # 2 minutes in seconds
        target_type=WorkoutStepTargetType.HEART_RATE
    ),
    
    # Cool-down step
    WorkoutStep(
        message_index=3,
        wkt_step_name="Cool Down",
        intensity=Intensity.COOLDOWN,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=600,  # 10 minutes in seconds
        target_type=WorkoutStepTargetType.OPEN
    )
]

# Create the complete workout
workout = Workout(
    file_id=file_id,
    workout=workout_msg,
    steps=steps
)

# Write to FIT file
write_fit_file(workout, "my_workout.fit")
```

### Reading a Workout

```python
from pysyfit.toolkit.converter import read_fit_file

# Read a FIT file
workout = read_fit_file("my_workout.fit")

# Access workout properties
print(f"Workout name: {workout.workout.wkt_name}")
print(f"Sport: {workout.workout.sport}")
print(f"Number of steps: {len(workout.steps)}")

# Access step properties
for i, step in enumerate(workout.steps):
    print(f"Step {i+1}: {step.wkt_step_name}")
    print(f"  Duration: {step.duration_type}")
    print(f"  Target: {step.target_type}")
```

## Workout Structure

A workout in PySyFit consists of:

1. **File ID Message**: Contains metadata about the file
2. **Workout Message**: Contains information about the workout itself
3. **Workout Steps**: Contains the individual steps that make up the workout

### Workout Step Types

PySyFit supports various workout step types:

- **Time**: Duration based on time
- **Distance**: Duration based on distance
- **Heart Rate**: Duration based on heart rate
- **Open**: Duration is open-ended
- **Repeat**: Repeat previous steps
- **Repetition Time**: Duration based on repetition time (for strength training)

### Target Types

PySyFit supports various target types:

- **Heart Rate**: Target a specific heart rate or zone
- **Power**: Target a specific power or zone
- **Cadence**: Target a specific cadence or zone
- **Speed**: Target a specific speed or zone
- **Open**: No specific target

## Advanced Usage

### Creating a Workout with Repeat Steps

```python
# Create a workout with repeat steps
steps = [
    # Warm-up step
    WorkoutStep(
        message_index=0,
        wkt_step_name="Warm Up",
        intensity=Intensity.WARMUP,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=300,  # 5 minutes in seconds
        target_type=WorkoutStepTargetType.OPEN
    ),
    
    # Main set - to be repeated
    WorkoutStep(
        message_index=1,
        wkt_step_name="Run Fast",
        intensity=Intensity.ACTIVE,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=60,  # 1 minute in seconds
        target_type=WorkoutStepTargetType.HEART_RATE,
        custom_target_heart_rate_low=160,
        custom_target_heart_rate_high=170
    ),
    
    # Recovery - to be repeated
    WorkoutStep(
        message_index=2,
        wkt_step_name="Recover",
        intensity=Intensity.REST,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=60,  # 1 minute in seconds
        target_type=WorkoutStepTargetType.HEART_RATE,
        custom_target_heart_rate_low=120,
        custom_target_heart_rate_high=130
    ),
    
    # Repeat step
    WorkoutStep(
        message_index=3,
        wkt_step_name="Repeat",
        intensity=Intensity.ACTIVE,
        duration_type=WorkoutStepDurationType.REPEAT_UNTIL_STEPS_CMPLT,
        duration_step=2,  # Repeat 2 steps
        duration_value=4,  # 4 times
        target_type=WorkoutStepTargetType.OPEN
    ),
    
    # Cool-down
    WorkoutStep(
        message_index=4,
        wkt_step_name="Cool Down",
        intensity=Intensity.COOLDOWN,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=300,  # 5 minutes in seconds
        target_type=WorkoutStepTargetType.OPEN
    )
]
```

### Creating a Cycling Power Workout

```python
# Create a cycling power workout
workout_msg = WorkoutMessage(
    wkt_name="Power Intervals",
    sport=Sport.CYCLING,
    num_valid_steps=4
)

steps = [
    # Warm-up step
    WorkoutStep(
        message_index=0,
        wkt_step_name="Warm Up",
        intensity=Intensity.WARMUP,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=600,  # 10 minutes in seconds
        target_type=WorkoutStepTargetType.POWER
    ),
    
    # Power Interval
    WorkoutStep(
        message_index=1,
        wkt_step_name="Power Interval",
        intensity=Intensity.ACTIVE,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=300,  # 5 minutes in seconds
        target_type=WorkoutStepTargetType.POWER,
        custom_target_power_low=250,
        custom_target_power_high=280
    ),
    
    # Recovery
    WorkoutStep(
        message_index=2,
        wkt_step_name="Recovery",
        intensity=Intensity.REST,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=180,  # 3 minutes in seconds
        target_type=WorkoutStepTargetType.POWER
    ),
    
    # Cool-down step
    WorkoutStep(
        message_index=3,
        wkt_step_name="Cool Down",
        intensity=Intensity.COOLDOWN,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=600,  # 10 minutes in seconds
        target_type=WorkoutStepTargetType.OPEN
    )
]
```

### Creating a Strength Training Workout

```python
# Create a strength training workout
workout_msg = WorkoutMessage(
    wkt_name="Full Body Strength",
    sport=Sport.TRAINING,
    num_valid_steps=5
)

steps = [
    # Warm-up step
    WorkoutStep(
        message_index=0,
        wkt_step_name="Warm Up",
        intensity=Intensity.WARMUP,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=300,  # 5 minutes in seconds
        target_type=WorkoutStepTargetType.OPEN
    ),
    
    # Exercise 1: Squats
    WorkoutStep(
        message_index=1,
        wkt_step_name="Squats",
        intensity=Intensity.ACTIVE,
        duration_type=WorkoutStepDurationType.REPETITION_TIME,
        duration_time=60,  # 1 minute in seconds
        target_type=WorkoutStepTargetType.OPEN
    ),
    
    # Rest
    WorkoutStep(
        message_index=2,
        wkt_step_name="Rest",
        intensity=Intensity.REST,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=30,  # 30 seconds
        target_type=WorkoutStepTargetType.OPEN
    ),
    
    # Exercise 2: Push-ups
    WorkoutStep(
        message_index=3,
        wkt_step_name="Push-ups",
        intensity=Intensity.ACTIVE,
        duration_type=WorkoutStepDurationType.REPETITION_TIME,
        duration_time=60,  # 1 minute in seconds
        target_type=WorkoutStepTargetType.OPEN
    ),
    
    # Cool-down
    WorkoutStep(
        message_index=4,
        wkt_step_name="Cool Down",
        intensity=Intensity.COOLDOWN,
        duration_type=WorkoutStepDurationType.TIME,
        duration_time=300,  # 5 minutes in seconds
        target_type=WorkoutStepTargetType.OPEN
    )
]
```

## API Reference

### Models

#### FileIdMessage

```python
class FileIdMessage(BaseModel):
    type: FileType = Field(default=FileType.WORKOUT)
    manufacturer: int = Field(default=0)
    product: int = Field(default=0)
    serial_number: Optional[int] = None
    time_created: datetime = Field(default_factory=datetime.now)
    number: Optional[int] = None
```

#### WorkoutMessage

```python
class WorkoutMessage(BaseModel):
    wkt_name: str = Field(default="")
    sport: Sport = Field(default=Sport.GENERIC)
    sub_sport: SubSport = Field(default=SubSport.GENERIC)
    num_valid_steps: int = Field(default=0)
```

#### WorkoutStep

```python
class WorkoutStep(BaseModel):
    message_index: int
    wkt_step_name: Optional[str] = None
    intensity: Intensity = Intensity.ACTIVE
    notes: Optional[str] = None
    duration_type: WorkoutStepDurationType
    duration_value: Optional[float] = None
    duration_time: Optional[float] = None  # in seconds
    duration_distance: Optional[float] = None  # in meters
    duration_hr: Optional[int] = None  # in bpm
    duration_calories: Optional[int] = None
    duration_step: Optional[int] = None  # for repeat steps
    duration_power: Optional[int] = None  # in watts
    target_type: WorkoutStepTargetType
    target_value: Optional[int] = None
    target_hr_zone: Optional[int] = None
    target_power_zone: Optional[int] = None
    target_stroke_type: Optional[int] = None
    target_speed_zone: Optional[int] = None
    target_cadence_zone: Optional[int] = None
    custom_target_heart_rate_low: Optional[int] = None
    custom_target_heart_rate_high: Optional[int] = None
    custom_target_speed_low: Optional[float] = None
    custom_target_speed_high: Optional[float] = None
    custom_target_power_low: Optional[int] = None
    custom_target_power_high: Optional[int] = None
    custom_target_cadence_low: Optional[int] = None
    custom_target_cadence_high: Optional[int] = None
```

#### Workout

```python
class Workout(BaseModel):
    file_id: FileIdMessage = Field(default_factory=FileIdMessage)
    workout: WorkoutMessage
    steps: List[WorkoutStep]
```

### Enumerations

#### Sport

```python
class Sport(IntEnum):
    GENERIC = 0
    RUNNING = 1
    CYCLING = 2
    TRANSITION = 3
    FITNESS_EQUIPMENT = 4
    SWIMMING = 5
    BASKETBALL = 6
    SOCCER = 7
    TENNIS = 8
    AMERICAN_FOOTBALL = 9
    TRAINING = 10
    # ... and many more
```

#### Intensity

```python
class Intensity(IntEnum):
    ACTIVE = 0
    REST = 1
    WARMUP = 2
    COOLDOWN = 3
```

#### WorkoutStepDurationType

```python
class WorkoutStepDurationType(IntEnum):
    TIME = 0
    DISTANCE = 1
    HR_LESS_THAN = 2
    HR_GREATER_THAN = 3
    CALORIES = 4
    OPEN = 5
    REPEAT_UNTIL_STEPS_CMPLT = 6
    REPEAT_UNTIL_TIME = 7
    REPEAT_UNTIL_DISTANCE = 8
    REPEAT_UNTIL_CALORIES = 9
    REPEAT_UNTIL_HR_LESS_THAN = 10
    REPEAT_UNTIL_HR_GREATER_THAN = 11
    REPEAT_UNTIL_POWER_LESS_THAN = 12
    REPEAT_UNTIL_POWER_GREATER_THAN = 13
    POWER_LESS_THAN = 14
    POWER_GREATER_THAN = 15
    REPETITION_TIME = 28
```

#### WorkoutStepTargetType

```python
class WorkoutStepTargetType(IntEnum):
    SPEED = 0
    HEART_RATE = 1
    OPEN = 2
    CADENCE = 3
    POWER = 4
    GRADE = 5
    RESISTANCE = 6
    POWER_3S = 7
    POWER_10S = 8
    POWER_30S = 9
    POWER_LAP = 10
    SWIM_STROKE = 11
    SPEED_LAP = 12
    HEART_RATE_LAP = 13
```

### Functions

#### read_fit_file

```python
def read_fit_file(file_path: str) -> Workout:
    """
    Read a FIT file and convert it to a Workout object.
    :param file_path: Path to the FIT file
    :return: Workout object containing the parsed data
    """
```

#### write_fit_file

```python
def write_fit_file(workout: Workout, file_path: str) -> None:
    """
    Write a Workout object to a FIT file.
    :param workout: The Workout object to write
    :param file_path: Path where the FIT file should be written
    :return: None
    """
```

## Compatibility

PySyFit generates FIT files that are compatible with:

- Garmin Connect
- TrainingPeaks
- Zwift
- Strava
- Most fitness devices that support FIT files

## Requirements

- Python 3.7+
- pydantic >= 2.0.0

## License

MIT License

## Acknowledgements

This library is based on the FIT protocol developed by Garmin. For more information about the FIT protocol, visit [Garmin's FIT SDK page](https://developer.garmin.com/fit/overview/).
