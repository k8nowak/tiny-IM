"""
This script is used to parse lesson contents from text files and convert them into JSON format. It extracts activities from the text and organizes them into a structured format. The script reads text files from an input folder, processes the contents, and writes the parsed data as JSON files to an output folder.
Functions:
- extract_activities(text): Extracts activities from the given text and returns a list of dictionaries representing each activity.
- parse_lesson(text): Parses the lesson contents from the given text and returns a dictionary containing the warm-up activity and a list of activity dictionaries.
"""

import os
import json

def extract_activities(text):
    activities = []
    current_activity = {}
    current_field = None
    lines = iter(text.splitlines())

    for line in lines:
        line = line.strip()

        # Check for timing in mins
        if line.endswith("mins") and line.split()[0].isdigit():
            if current_activity:
                activities.append(current_activity)
            current_activity = {"activity_timing_mins": int(line.split()[0])}
            current_field = None
        
        elif line.startswith("## Warm-up") or line.startswith("## Activity"):
            # Move to the next line to get the actual title
            next_line = next(lines).strip()
            current_activity["activity_title"] = next_line.replace("### ", "")
            current_field = None
        
        elif line.startswith("### Activity Narrative"):
            current_field = "activity_narrative"
            current_activity[current_field] = ""
        
        elif line.startswith("### Launch"):
            current_field = "launch"
            current_activity[current_field] = ""
        
        elif line.startswith("### Student Task Statement"):
            current_field = "student_task_statement"
            current_activity[current_field] = ""
        
        elif line.startswith("### Activity Synthesis"):
            current_field = "activity_synthesis"
            current_activity[current_field] = ""

        # Detect unwanted subsections and stop adding to the current field
        elif line.startswith("### ") and current_field:
            current_field = None  # Stop adding content to the current field

        elif current_field:
            if current_activity[current_field]:
                current_activity[current_field] += " " + line
            else:
                current_activity[current_field] = line

    if current_activity:
        activities.append(current_activity)

    return activities

def parse_lesson(text):
    activities = extract_activities(text)
    return {
        "warm_up": activities[0] if activities else {},
        "activities": activities[1:] if len(activities) > 1 else []
    }

if __name__ == "__main__":
    input_folder = "lesson_contents_b"
    output_folder = "lesson_contents_c"

    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all text files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            # Construct full file path
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename.replace(".txt", ".json"))

            # Read the text file
            with open(input_file_path, "r") as file:
                text = file.read()

            # Parse the lesson and convert it to JSON
            lesson_data = parse_lesson(text)

            # Write the JSON to the output folder
            with open(output_file_path, "w") as json_file:
                json.dump(lesson_data, json_file, indent=4)

            print(f"JSON data written to {output_file_path}")
