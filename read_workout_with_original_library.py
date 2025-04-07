

if __name__ == "__main__":
    # Create output directory
    import os
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    running_output_path = os.path.join(output_dir, "running_interval_workout.fit")


    from garmin_fit_sdk import Decoder, Stream

    stream = Stream.from_file(running_output_path)
    decoder = Decoder(stream)
    messages, errors = decoder.read()
    print("=== Errors ===")
    print(errors)
    print("=== Messages ===")
    print(messages)