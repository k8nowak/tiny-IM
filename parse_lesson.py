import json
import re

def extract_lines_between(lines, start_key, end_key):
    try:
        start_index = lines.index(start_key) + 1
        end_index = lines.index(end_key) if end_key else len(lines)
        return lines[start_index:end_index]
    except ValueError:
        return []

def parse_multiline_section(lines):
    return "\n".join(lines).strip() if lines else None

def parse_list_section(lines):
    return [line for line in lines if line.strip()] or None

def parse_activity(lines):
    activity = {}
    current_section = None
    narrative = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if re.match(r"^\d+ mins$", line):
            activity["time"] = int(line.split()[0])
        elif line in ["Activity Narrative", "Launch", "Student Task Statement", "Activity Synthesis"]:
            if current_section and narrative:
                activity[current_section] = "\n".join(narrative).strip()
            current_section = line
            narrative = []
        elif line == "Launch" and i + 1 < len(lines):
                current_section="Launch"
                narrative=[]
                
        elif line == "Activity Narrative" and i - 1 >= 0:
            activity["title"] = lines[i - 1].strip()
        elif current_section is None and i > 0 and re.match(r"^\d+ mins$", lines[i-1]):
            activity["title"] = lines[i+1].strip()
        elif line == "Student Task Statement" and current_section == "Launch":
            # Finish the Launch section when reaching the Student Task Statement
            activity["Launch"] = "\n".join(narrative).strip()
            current_section = "Student Task Statement"
            narrative = []
        else:
            narrative.append(line)
    
    if current_section and narrative:
        activity[current_section] = "\n".join(narrative).strip()
    
    return activity



def parse_lesson_content(lines):
    content = {
        "activities": []
    }
    activity_start = "Lesson Content"
    activity_lines = extract_lines_between(lines, activity_start, None)
    
    for i, line in enumerate(activity_lines):
        if re.match(r"^\d+ mins$", line):
            time = int(line.split()[0])
            activity = parse_activity(activity_lines[i:])
            activity["time"] = time
            content["activities"].append(activity)
    
    return content

def process_file(filename):
    with open(filename, "r") as file:
        lines = [line.strip() for line in file.readlines()]
    
    json_data = {
        "unitNumber": lines[0].split()[1],
        "unitTitle": lines[1],
        "lessonNumber": lines[2].split()[1],
        "lessonTitle": lines[3],
        "lessonNarrative": parse_multiline_section(extract_lines_between(lines, "Lesson Narrative", "Learning Goals")),
        "learningGoals": parse_list_section(extract_lines_between(lines, "Learning Goals", "Student-Facing Goal")),
        "studentFacingGoal": parse_multiline_section(extract_lines_between(lines, "Student-Facing Goal", "Student-Facing Targets")),
        "studentFacingTargets": parse_list_section(extract_lines_between(lines, "Student-Facing Targets", "Required Preparation")),
        "requiredPreparation": parse_multiline_section(extract_lines_between(lines, "Required Preparation", "Standards Alignment")),
        "standardsAlignment": {
            "buildingOn": parse_list_section(extract_lines_between(lines, "Building On", "Addressing")),
            "addressing": parse_list_section(extract_lines_between(lines, "Addressing", "Building Toward")),
            "buildingToward": parse_list_section(extract_lines_between(lines, "Building Toward", "Lesson Content"))
        },
        "lessonContent": parse_lesson_content(lines),
        "lessonSynthesis": parse_multiline_section(extract_lines_between(lines, "Lesson Synthesis", "Student Lesson Summary")),
        "studentLessonSummary": parse_multiline_section(extract_lines_between(lines, "Student Lesson Summary", None))
    }
    
    return json_data

def save_json(data, output_filename):
    with open(output_filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Example usage:
input_filename = "lesson_contents/Comparing_Graphs.txt"  # Replace with your actual file path
output_filename = "lesson_output.json"

lesson_json = process_file(input_filename)
save_json(lesson_json, output_filename)

print(f"Lesson plan successfully processed and saved to {output_filename}")
