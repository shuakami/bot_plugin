import os
import sys

def validate_pr_structure():
    # Define expected file structure
    expected_files = [
        'plugin_name.zip',
        'checksum.txt',
        'plugin_name.jpg',  # or plugin_name.png
        'plugin_name.json'
    ]
    
    # Extract PR directory from the environment or assume a default
    pr_directory = '.'
    
    # Check if each expected file exists
    missing_files = []
    for expected_file in expected_files:
        if not os.path.exists(os.path.join(pr_directory, expected_file)):
            missing_files.append(expected_file)
    
    if missing_files:
        print(f"Error: Missing required files in PR: {', '.join(missing_files)}")
        sys.exit(1)  # Fail the action
    else:
        print("PR structure validation passed.")
        sys.exit(0)  # Success

if __name__ == '__main__':
    validate_pr_structure()
