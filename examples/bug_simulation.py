import traceback

import pandas as pd

from preswald.engine.runner import validate_dataframe_operation


def simulate_bug_and_fix():
    """
    Simulate the original bug and demonstrate our fix.
    """
    print("🔍 Bug Simulation: Column 'value' not found in DataFrame")
    print("==================================================")

    # Create a sample DataFrame (similar to the weather data)
    df = pd.DataFrame(
        {
            "Humidity": [0.81, 0.76, 0.68, 0.92, 0.95],
            "Temperature": [21.2, 22.1, 19.5, 18.7, 16.3],
            "Summary": ["Partly Cloudy", "Mostly Cloudy", "Clear", "Foggy", "Rain"],
        }
    )

    print("\n📊 Sample DataFrame:")
    print(df.head())
    print("\n📋 Available columns:", ", ".join(df.columns))

    # Scenario 1: Original bug - trying to access 'value' column
    print("\n❌ Scenario 1: Original bug - trying to access 'value' column")
    threshold = 50
    try:
        # This would fail with a cryptic error
        filtered_data = df[df["value"] > threshold]
        print(filtered_data)  # This line won't execute
    except Exception as e:
        print(f"Error: {e}")
        print("Traceback:", "".join(traceback.format_tb(e.__traceback__)))

    # Scenario 2: With our fix - validation before operation
    print("\n✅ Scenario 2: With our fix - validation before operation")
    threshold = 50
    try:
        # This will fail with a helpful error message
        validate_dataframe_operation(df, "value", "filtering")
        filtered_data = df[df["value"] > threshold]
        print(filtered_data)  # This line won't execute
    except ValueError as e:
        print(f"Error: {e}")

    # Scenario 3: Correct usage
    print("\n✅ Scenario 3: Correct usage with valid column")
    humidity_threshold = 0.8
    try:
        validate_dataframe_operation(df, "Humidity", "filtering")
        filtered_data = df[df["Humidity"] > humidity_threshold]
        print(filtered_data)
    except Exception as e:
        print(f"Error: {e}")

    print("\n🎯 Summary of fixes:")
    print("1. Added early validation of DataFrame operations")
    print("2. Improved error messages with available columns")
    print("3. Made error handling consistent between preview and published modes")
    print("4. Added helpful suggestions to guide users")


if __name__ == "__main__":
    simulate_bug_and_fix()
