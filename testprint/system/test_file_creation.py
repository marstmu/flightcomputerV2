import os

# Define the test directory and file names
dir_name = "/data"
file_name = "blank_file.txt"
file_path = dir_name + "/" + file_name

# Function to create the directory if it doesn't exist
def create_directory_if_needed(directory):
    try:
        # List directories to check if 'data' exists
        if directory not in os.listdir("/"):
            print(f"Creating directory: {directory}")
            os.mkdir(directory)
        else:
            print(f"Directory '{directory}' already exists.")
    except Exception as e:
        print(f"Error creating directory: {e}")

# Function to create the blank file
def create_blank_file(filepath):
    try:
        with open(filepath, "w") as file:
            pass  # Create a blank file
        print(f"Blank file created at: {filepath}")
    except Exception as e:
        print(f"Error creating file: {e}")

# Main function
def main():
    # Ensure the directory exists
    create_directory_if_needed(dir_name)
    
    # Create the blank file in the 'data' directory
    create_blank_file(file_path)

# Run the main function
main()
