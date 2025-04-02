from enum import IntEnum


class FileType(IntEnum):
    """File type values from FIT protocol."""
    ACTIVITY = 4
    WORKOUT = 5
    COURSE = 6


class Sport(IntEnum):
    """Sport type values from FIT protocol."""
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
    WALKING = 11
    CROSS_COUNTRY_SKIING = 12
    ALPINE_SKIING = 13
    SNOWBOARDING = 14
    ROWING = 15
    MOUNTAINEERING = 16
    HIKING = 17
    MULTISPORT = 18
    PADDLING = 19
    FLYING = 20
    E_BIKING = 21
    MOTORCYCLING = 22
    BOATING = 23
    DRIVING = 24
    GOLF = 25
    HANG_GLIDING = 26
    HORSEBACK_RIDING = 27
    HUNTING = 28
    FISHING = 29
    INLINE_SKATING = 30
    ROCK_CLIMBING = 31
    SAILING = 32
    ICE_SKATING = 33
    SKY_DIVING = 34
    SNOWSHOEING = 35
    SNOWMOBILING = 36
    STAND_UP_PADDLEBOARDING = 37
    SURFING = 38
    WAKEBOARDING = 39
    WATER_SKIING = 40
    KAYAKING = 41
    RAFTING = 42
    WINDSURFING = 43
    KITESURFING = 44
    TACTICAL = 45
    JUMPMASTER = 46
    BOXING = 47
    FLOOR_CLIMBING = 48
    ALL = 254


class SubSport(IntEnum):
    """Sub-sport type values from FIT protocol."""
    GENERIC = 0
    TREADMILL = 1  # Running
    STREET = 2  # Running
    TRAIL = 3  # Running
    TRACK = 4  # Running
    SPIN = 5  # Cycling
    INDOOR_CYCLING = 6  # Cycling
    ROAD = 7  # Cycling
    MOUNTAIN = 8  # Cycling
    DOWNHILL = 9  # Cycling
    RECUMBENT = 10  # Cycling
    CYCLOCROSS = 11  # Cycling
    HAND_CYCLING = 12  # Cycling
    TRACK_CYCLING = 13  # Cycling
    INDOOR_ROWING = 14  # Fitness Equipment
    ELLIPTICAL = 15  # Fitness Equipment
    STAIR_CLIMBING = 16  # Fitness Equipment
    LAP_SWIMMING = 17  # Swimming
    OPEN_WATER = 18  # Swimming
    FLEXIBILITY_TRAINING = 19  # Training
    STRENGTH_TRAINING = 20  # Training
    WARM_UP = 21  # Tennis
    MATCH = 22  # Tennis
    EXERCISE = 23  # Tennis
    CHALLENGE = 24
    INDOOR_SKIING = 25  # Fitness Equipment
    CARDIO_TRAINING = 26  # Training
    INDOOR_WALKING = 27  # Walking
    E_BIKE_FITNESS = 28  # E-Biking
    BMX = 29  # Cycling
    CASUAL_WALKING = 30  # Walking
    SPEED_WALKING = 31  # Walking
    BIKE_TO_RUN_TRANSITION = 32  # Transition
    RUN_TO_BIKE_TRANSITION = 33  # Transition
    SWIM_TO_BIKE_TRANSITION = 34  # Transition
    ATV = 35  # Motorcycling
    MOTOCROSS = 36  # Motorcycling
    BACKCOUNTRY = 37  # Alpine Skiing/Snowboarding
    RESORT = 38  # Alpine Skiing/Snowboarding
    RC_DRONE = 39  # Flying
    WINGSUIT = 40  # Flying
    WHITEWATER = 41  # Kayaking/Rafting
    SKATE_SKIING = 42  # Cross Country Skiing
    YOGA = 43  # Training
    PILATES = 44  # Fitness Equipment
    INDOOR_RUNNING = 45  # Running
    GRAVEL_CYCLING = 46  # Cycling
    E_BIKE_MOUNTAIN = 47  # Cycling
    COMMUTING = 48  # Cycling
    MIXED_SURFACE = 49  # Cycling
    NAVIGATE = 50
    TRACK_ME = 51
    MAP = 52
    SINGLE_GAS_DIVING = 53  # Diving
    MULTI_GAS_DIVING = 54  # Diving
    GAUGE_DIVING = 55  # Diving
    APNEA_DIVING = 56  # Diving
    APNEA_HUNTING = 57  # Diving
    VIRTUAL_ACTIVITY = 58
    OBSTACLE = 59  # Used for events where participants run, crawl through mud, climb over walls, etc.
    BREATHING = 62
    SAIL_RACE = 65  # Sailing
    ULTRA = 67  # Ultra run/trail
    INDOOR_CLIMBING = 68  # Rock climbing
    BOULDERING = 69  # Rock climbing
    HIIT = 70  # High Intensity Interval Training
    AMRAP = 73  # HIIT: As Many Rounds as Possible
    EMOM = 74  # HIIT: Every Minute on the Minute
    TABATA = 75  # HIIT: 20 sec activity, 10 sec rest, repeat
    CLIMBING = 77  # Rock climbing
    ALL = 254


class Intensity(IntEnum):
    """Intensity values from FIT protocol."""
    ACTIVE = 0
    REST = 1
    WARMUP = 2
    COOLDOWN = 3


class WorkoutStepDurationType(IntEnum):
    """Duration type values for workout steps from FIT protocol."""
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


class WorkoutStepTargetType(IntEnum):
    """Target type values for workout steps from FIT protocol."""
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
