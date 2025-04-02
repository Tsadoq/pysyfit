from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

from pysyfit.models.enum_types import WorkoutStepTargetType, WorkoutStepDurationType, Intensity, FileType, Sport, \
    SubSport


class FileIdMessage(BaseModel):
    """
    File ID message as defined in FIT protocol.
    Required as the first message in every FIT file.
    """
    type: FileType = Field(default=FileType.WORKOUT)
    manufacturer: int = Field(default=0)
    product: int = Field(default=0)
    serial_number: Optional[int] = None
    time_created: datetime = Field(default_factory=datetime.now)
    number: Optional[int] = None


class WorkoutMessage(BaseModel):
    """
    Workout message as defined in FIT protocol.
    Provides a summary of the workout and the number of valid steps.
    """
    wkt_name: str = Field(default="")
    sport: Sport = Field(default=Sport.GENERIC)
    sub_sport: SubSport = Field(default=SubSport.GENERIC)
    num_valid_steps: int = Field(default=0)
    
    @field_validator('wkt_name')
    def validate_name_length(cls, v):
        """Validate that the workout name is not too long."""
        if len(v) > 16:  # FIT protocol typically limits string fields
            return v[:16]
        return v


class WorkoutStepBase(BaseModel):
    """
    Base class for workout steps with common fields.
    """
    message_index: int
    wkt_step_name: Optional[str] = None
    intensity: Intensity = Intensity.ACTIVE
    notes: Optional[str] = None


class WorkoutStepDuration(BaseModel):
    """
    Duration component of a workout step.
    Defines how long the step lasts or when it ends.
    """
    duration_type: WorkoutStepDurationType
    duration_value: Optional[float] = None
    duration_time: Optional[float] = None  # in seconds
    duration_distance: Optional[float] = None  # in meters
    duration_hr: Optional[int] = None  # in bpm
    duration_calories: Optional[int] = None
    duration_step: Optional[int] = None  # for repeat steps
    duration_power: Optional[int] = None  # in watts
    
    @field_validator('duration_value')
    def validate_duration_value(cls, v, values):
        """Ensure duration_value is set based on the specific duration type field."""
        if v is not None:
            return v
            
        duration_type = values.get('duration_type')
        
        if duration_type == WorkoutStepDurationType.TIME and values.get('duration_time') is not None:
            return values.get('duration_time')
        elif duration_type == WorkoutStepDurationType.DISTANCE and values.get('duration_distance') is not None:
            return values.get('duration_distance')
        elif duration_type in [WorkoutStepDurationType.HR_LESS_THAN, WorkoutStepDurationType.HR_GREATER_THAN] and values.get('duration_hr') is not None:
            return values.get('duration_hr')
        elif duration_type == WorkoutStepDurationType.CALORIES and values.get('duration_calories') is not None:
            return values.get('duration_calories')
        elif duration_type in [WorkoutStepDurationType.REPEAT_UNTIL_STEPS_CMPLT] and values.get('duration_step') is not None:
            return values.get('duration_step')
        elif duration_type in [WorkoutStepDurationType.POWER_LESS_THAN, WorkoutStepDurationType.POWER_GREATER_THAN] and values.get('duration_power') is not None:
            return values.get('duration_power')
        
        # For OPEN duration type, no value is needed
        if duration_type == WorkoutStepDurationType.OPEN:
            return None
            
        return v


class WorkoutStepTarget(BaseModel):
    """
    Target component of a workout step.
    Defines what the user should aim for during the step.
    """
    target_type: WorkoutStepTargetType
    target_value: Optional[int] = None
    target_hr_zone: Optional[int] = None
    target_power_zone: Optional[int] = None
    target_stroke_type: Optional[int] = None
    target_speed_zone: Optional[int] = None
    target_cadence_zone: Optional[int] = None
    
    # Custom target values for specific ranges
    custom_target_heart_rate_low: Optional[int] = None
    custom_target_heart_rate_high: Optional[int] = None
    custom_target_speed_low: Optional[float] = None
    custom_target_speed_high: Optional[float] = None
    custom_target_power_low: Optional[int] = None
    custom_target_power_high: Optional[int] = None
    custom_target_cadence_low: Optional[int] = None
    custom_target_cadence_high: Optional[int] = None
    
    @field_validator('target_value')
    def validate_target_value(cls, v, values):
        """Ensure target_value is set based on the specific target type field."""
        if v is not None:
            return v
            
        target_type = values.get('target_type')
        
        if target_type == WorkoutStepTargetType.HEART_RATE and values.get('target_hr_zone') is not None:
            return values.get('target_hr_zone')
        elif target_type == WorkoutStepTargetType.POWER and values.get('target_power_zone') is not None:
            return values.get('target_power_zone')
        elif target_type == WorkoutStepTargetType.CADENCE and values.get('target_cadence_zone') is not None:
            return values.get('target_cadence_zone')
        elif target_type == WorkoutStepTargetType.SPEED and values.get('target_speed_zone') is not None:
            return values.get('target_speed_zone')
        elif target_type == WorkoutStepTargetType.SWIM_STROKE and values.get('target_stroke_type') is not None:
            return values.get('target_stroke_type')
        
        # For OPEN target type, no value is needed
        if target_type == WorkoutStepTargetType.OPEN:
            return None
            
        return v


class WorkoutStep(WorkoutStepBase, WorkoutStepDuration, WorkoutStepTarget):
    """
    Complete workout step combining base information, duration, and target.
    """
    
    @field_validator('message_index')
    def validate_message_index(cls, v):
        """Ensure message_index is non-negative."""
        if v < 0:
            raise ValueError("message_index must be non-negative")
        return v
    
    @field_validator('wkt_step_name')
    def validate_step_name_length(cls, v):
        """Validate that the step name is not too long."""
        if v is not None and len(v) > 16:  # FIT protocol typically limits string fields
            return v[:16]
        return v


class Workout(BaseModel):
    """
    Complete workout definition including file ID, workout message, and steps.
    """
    file_id: FileIdMessage = Field(default_factory=FileIdMessage)
    workout: WorkoutMessage
    steps: List[WorkoutStep]

    @model_validator(mode="after")
    def check_a_equals_b(cls, model: "Workout") -> "Workout":
        """Ensure num_valid_steps matches the number of steps."""
        if model.workout.num_valid_steps == len(model.steps):
            raise ValueError("The values of 'a' and 'b' must be the same")
        return model

    @field_validator('steps')
    def validate_steps(cls, v):
        """Ensure steps have sequential message_index values."""
        if not v:
            return v
            
        # Sort steps by message_index if they're not in order
        sorted_steps = sorted(v, key=lambda step: step.message_index)
        
        # Reassign message_index values to ensure they're sequential
        for i, step in enumerate(sorted_steps):
            step.message_index = i
            
        return sorted_steps
