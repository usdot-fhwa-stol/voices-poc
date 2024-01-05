import os
import sys
import shutil
import subprocess

def select_data_folder(input_dir):
    folders = [folder for folder in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, folder))]

    if not folders:
        print("No folders found in the current directory.")
        return None

    print("\nSelect a folder to export:")
    for index, folder in enumerate(folders, start=1):
        print(f"\t{index}. {folder}")
    
    while True:
        try:
            user_choice = input("\nSelect a folder by entering the corresponding number (leave empty to use current directory): ")
            if user_choice == '':
                absolute_path = input_dir
            else:
                selected_folder = folders[int(user_choice) - 1]
                absolute_path = os.path.abspath(os.path.join(input_dir, selected_folder))
                
            return absolute_path

        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid number.")

def create_export_folder(directory):
    exported_folder_path = os.path.join(directory, "exported_tdcs")

    # Check if the folder already exists
    if os.path.exists(exported_folder_path):
        try:
            # Confirm with the user before deleting
            confirmation = input(f"Exsisting TDCS export folder found, delete old data? (y/n): ").lower()

            if confirmation == 'y':
                # Use shutil.rmtree to delete the folder and its contents
                shutil.rmtree(exported_folder_path)
                print(f"Folder '{exported_folder_path}' deleted successfully.")

                try:
                    os.makedirs(exported_folder_path)
                    print(f"Created 'exported_tdcs' folder in {directory}")
                except OSError as e:
                    print(f"Error creating folder in {directory}: {e}")
            else:
                print("Keeping old data.")
                return True

        except Exception as e:
            print(f"Error deleting folder: {e}")
            sys.exit()

    else:  
        try:
            os.makedirs(exported_folder_path)
            print(f"Created 'exported_tdcs' folder in {directory}")
        except OSError as e:
            print(f"Error creating folder in {directory}: {e}")

def find_largest_sqlite_file(folder_path):
    # Get a list of files in the specified folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Filter files with ".sqlite" extension
    sqlite_files = [f for f in files if f.endswith('.sqlite')]

    if not sqlite_files:
        print("No .sqlite files found in the specified folder.")
        return None

    # Find the largest .sqlite file
    largest_file = max(sqlite_files, key=lambda f: os.path.getsize(os.path.join(folder_path, f)))

    # Return the absolute path of the largest .sqlite file
    print("\tUsing sqlite file: " + largest_file)
    return os.path.abspath(os.path.join(folder_path, largest_file))

def main(): 
    dataview_dir = "/opt/TENA/DataView-v1.5.4/start.sh"

    start_log_dir = os.environ["VUG_LOG_FILES_ROOT"]
    current_log_dir = start_log_dir
    chosen_log_dir = None

    while True:
        chosen_log_dir = select_data_folder(current_log_dir)
        if chosen_log_dir == current_log_dir:
            break
        else:
            current_log_dir = chosen_log_dir

    if chosen_log_dir:
        print(f"Selected folder: {chosen_log_dir}")

        # create_export_folder(chosen_log_dir)

    # Get a list of all directories in the given parent directory
    site_dirs = [entry for entry in os.listdir(chosen_log_dir) if os.path.isdir(os.path.join(chosen_log_dir, entry))]

    # Iterate through each directory and create "exported_tdcs" folder
    for site_dir in site_dirs:
        print ("\nExporting: " + site_dir)
        site_dir_abs = os.path.join(chosen_log_dir, site_dir)

        skip_export = create_export_folder(site_dir_abs)
        if not skip_export:
            tdcs_file_path = find_largest_sqlite_file(site_dir_abs)
            os.chdir(site_dir_abs)
            try:
                tdcs_cmd = dataview_dir + " -d " + tdcs_file_path
                subprocess.run(tdcs_cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running the program: {e}")

if __name__ == "__main__":
    main()


