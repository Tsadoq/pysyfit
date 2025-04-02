"""
Main test script for the FIT workout library.

This script tests the functionality of the FIT workout library by:
1. Reading example FIT files
2. Creating a sample workout
3. Writing the sample workout to a FIT file
4. Performing round-trip conversion tests
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the fitlib package
sys.path.append(str(Path(__file__).parent.parent))

from fitlib.models import (
    FileType, Sport, SubSport, Intensity,
    WorkoutStepDurationType, WorkoutStepTargetType,
    FileIdMessage, WorkoutMessage, WorkoutStep, Workout
)
from fitlib.converter import read_fit_file, write_fit_file
from fitlib.test_converter import (
    test_read_fit_file, test_write_fit_file, 
    test_roundtrip, create_sample_workout
)


def main():
    """Main test function."""
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Test reading example FIT files
    example_files = [
        "/home/ubuntu/upload/WorkoutIndividualSteps.fit",
        "/home/ubuntu/upload/WorkoutCustomTargetValues.fit",
        "/home/ubuntu/upload/WorkoutRepeatSteps.fit",
        "/home/ubuntu/upload/WorkoutRepeatGreaterThanStep.fit"
    ]
    
    print("=== Testing Reading Example FIT Files ===")
    for file_path in example_files:
        print(f"\nReading {os.path.basename(file_path)}")
        workout = test_read_fit_file(file_path)
        if workout:
            print(f"Successfully read {os.path.basename(file_path)}")
    
    # Create and write a sample workout
    print("\n=== Testing Creating and Writing a Sample Workout ===")
    sample_workout = create_sample_workout()
    sample_output_path = output_dir / "sample_workout.fit"
    success = test_write_fit_file(sample_workout, sample_output_path)
    
    if success:
        print(f"Successfully created and wrote sample workout to {sample_output_path}")
        
        # Test reading the sample workout
        print("\nReading the sample workout")
        test_read_fit_file(sample_output_path)
    
    # Test round-trip conversion
    print("\n=== Testing Round-Trip Conversion ===")
    for file_path in example_files:
        print(f"\nRound-trip test for {os.path.basename(file_path)}")
        output_path = output_dir / f"roundtrip_{os.path.basename(file_path)}"
        success, input_workout, output_workout, _ = test_roundtrip(file_path, output_dir)
        
        if success:
            print(f"Successfully performed round-trip conversion for {os.path.basename(file_path)}")
    
    print("\nAll tests completed.")


if __name__ == "__main__":
    main()
