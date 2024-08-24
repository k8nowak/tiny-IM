"""
This script deletes specific lines from text files in the input directory and saves the modified files in the output directory. It removes the lines that match the phrases specified in the 'phrases_to_delete' list. Additionally, it keeps only the first occurrence of lines that match the phrases specified in the 'phrases_to_keep_once' list. The script processes all text files in the input directory and creates corresponding modified files in the output directory.
Parameters:
    input_dir (str): The directory path where the input text files are located.
    output_dir (str): The directory path where the modified text files will be saved.
Returns:
    None: The function saves the modified text files in the output directory.
"""

import os
import glob

# Define the input and output directories
input_dir = 'lesson_contents/'
output_dir = 'lesson_contents_b/'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)



# Define the list of phrases to delete
phrases_to_delete = [
    '### Activity',
    '#### Student response',
    '### Student Response',
    '## Preparation',
    'Practice', 
    '### Other Resources', 
    'View Student Lesson', 
    '## Teacher Support', 
    '## Student Handouts', 
    '### Instructional Routines',
    '### Materials',
    '#### To Copy (from Blackline Masters)',
    '#### To Gather'
]

# Phrases to keep only the first occurrence of
phrases_to_keep_once = [
    '### Standards Alignment',
    '#### Building On',
    '#### Addressing',
    '#### Building Toward'
]


# Loop through all text files in the input directory
for input_file in glob.glob(os.path.join(input_dir, '*.txt')):
    # Get the base name of the file (without the directory)
    base_name = os.path.basename(input_file)
    # Define the output file path
    output_file = os.path.join(output_dir, base_name)
    
    # Dictionary to track if these phrases have been seen before
    seen_phrases = {phrase: False for phrase in phrases_to_keep_once}

    # Open the input file and create an output file
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        # Loop through each line in the file
        for line in infile:
            stripped_line = line.strip()

            # If the line matches a phrase to delete, skip it
            if stripped_line in phrases_to_delete:
                continue
            
            # If the line matches a phrase to keep only once
            if stripped_line in phrases_to_keep_once:
                # If we haven't seen this phrase before, write it and mark as seen
                if not seen_phrases[stripped_line]:
                    outfile.write(line)
                    seen_phrases[stripped_line] = True
                # Otherwise, skip the line
                continue

            # If the line doesn't match any of the phrases to delete, write it to the output file
            outfile.write(line)

    print(f"Processed {input_file} -> {output_file}")

print("Processing complete. Check the output folder for the results.")