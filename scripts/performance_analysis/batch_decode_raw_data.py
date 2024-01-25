import os
import sys
import shutil
import subprocess
import json
from datetime import datetime
import csv
import re


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

def create_folder(directory_path,directory_name):
    exported_folder_path = os.path.join(directory_path, directory_name)

    # Check if the folder already exists
    if os.path.exists(exported_folder_path):
        try:
            # Confirm with the user before deleting
            confirmation = input(f"\nExsisting TDCS export folder found, delete old data and re-export? (y/n): ").lower()

            if confirmation == 'y':
                # Use shutil.rmtree to delete the folder and its contents
                shutil.rmtree(exported_folder_path)
                print(f"Folder '{exported_folder_path}' deleted successfully.")

                try:
                    os.makedirs(exported_folder_path)
                    print(f"Created {directory_name} folder in {directory_path}")
                except OSError as e:
                    print(f"Error creating folder in {directory_path}: {e}")
            else:
                print("Keeping old data.")
                return True

        except Exception as e:
            print(f"Error deleting folder: {e}")
            sys.exit()

    else:  
        try:
            os.makedirs(exported_folder_path)
            print(f"Created {directory_name} folder in {directory_path}")
        except OSError as e:
            print(f"Error creating folder in {directory_path}: {e}")

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

def get_epoch_time():

    while True:
        try:
            user_input = input("\n\t -->  ")
            # Convert user input to datetime object
            input_datetime = datetime.strptime(user_input, "%Y-%m-%d %H:%M:%S")

            # Convert datetime object to epoch time
            epoch_time = int(input_datetime.timestamp())
            
            return epoch_time
        except ValueError:
            print("\nInvalid date format. Please use YYYY-MM-DD HH:MM:SS.")

def get_obj_by_key_value(obj_array,key,value):
    for index, element in enumerate(obj_array):
        if element[key] == value:
            return element
    return None

def get_site_type():
    site_types = ["live","virtual","constructive","v2xhub"]
    

    while True:
        print("\nSelect site type:")
        for index, site_type in enumerate(site_types, start=1):
            print(f"\t{index}. {site_type}")

        try:
            site_choice = input("\nSelect a site type by entering the corresponding number: ")
            selected_site_type = site_types[int(site_choice) - 1]
                
            return selected_site_type

        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid number.")

def remove_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        print(f"Error removing file: {e}")
        sys.exit()

def get_adapter_addresses_by_type(exported_tcs_path,ip_address):

    try:
        # Get a list of all files in the specified directory
        exported_tdcs_files = [f for f in os.listdir(exported_tcs_path) if os.path.isfile(os.path.join(exported_tcs_path, f))]
        print(str(exported_tdcs_files))
    except FileNotFoundError:
        return f"Error: Directory not found - {exported_tcs_path}"
    except Exception as e:
        return f"Exception getting list of exported TDCS data: {e}"
    
    adapter_addresses_by_type = {}

    for file in exported_tdcs_files:
        print(f"\tChecking {file}")
        file_path = os.path.join(exported_tcs_path,file)

        pattern = re.compile(r'VUG-(.*?)-202')
        match = pattern.search(file)
        
        if match:
            msg_type = match.group(1)
        else:
            print("\nERROR: Unable to get message type from: " + file)

        try:
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                headers = reader.fieldnames
                
                if "Metadata,Endpoint" in headers:
                    endpoint_col = "Metadata,Endpoint"
                elif "const^Metadata,Endpoint" in headers:
                    endpoint_col = "const^Metadata,Endpoint"
                else:
                    print(f"Error: unable to locate endpoint column in file: {csvfile}")
                # Assuming the CSV file has a column named "const^Metadata,Endpoint"
                for row in reader:

                    if ip_address in row[endpoint_col]:
                        adapter_addresses_by_type[msg_type] = row[endpoint_col]
                        
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
            sys.exit()
        except Exception as e:
            print(f"Exception reading file ({file_path}): {e}")
            sys.exit()
    
    return adapter_addresses_by_type


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

    use_existing_metadata = "n"
    
    metadata_file_path = os.path.join(chosen_log_dir, "metadata.json")

    if os.path.exists(metadata_file_path):
        use_existing_metadata = input("\nExisting metadata file found, use existing data? [y/n] ").lower()

        if use_existing_metadata == 'y':
            print("")
            with open(metadata_file_path, 'r') as metadata_file:
 
                # Reading from json file
                metadata_json = json.load(metadata_file)
            start_time = metadata_json[0]["start_time"]
            end_time = metadata_json[0]["end_time"]
            
        else:
            remove_file(metadata_file_path)

            print ("\nEnter the event start time (YYYY-MM-DD HH:MM:SS): ")
            start_time = get_epoch_time()

            print ("\nEnter the event end time (YYYY-MM-DD HH:MM:SS): ")
            end_time = get_epoch_time()
    else:
        print ("\nEnter the event start time (YYYY-MM-DD HH:MM:SS): ")
        start_time = get_epoch_time()

        print ("\nEnter the event end time (YYYY-MM-DD HH:MM:SS): ")
        end_time = get_epoch_time()

       


    

    # Get a list of all directories in the given parent directory
    site_dirs = [entry for entry in os.listdir(chosen_log_dir) if os.path.isdir(os.path.join(chosen_log_dir, entry))]

    metatada = []

    # Iterate through each directory and create "exported_tdcs" folder
    for site_dir in site_dirs:
        print ("\nExporting: " + site_dir)
        site_dir_abs = os.path.join(chosen_log_dir, site_dir)

        this_site_metadata = None
        

        if use_existing_metadata == 'y':
            this_site_metadata = get_obj_by_key_value(metadata_json,"site_name",site_dir)
            print(f'this_site_metadata {this_site_metadata}')
        
        if this_site_metadata == None:
            
            this_site_metadata = {
                "site_name" : site_dir,
                "is_v2xhub" : None,
                "lvc" : None,
                "tdcs_dir" : None,
                "pcap_in_dir" : None,
                "pcap_out_dir" : None,
                "start_time" : start_time,
                "end_time" : end_time,
                "ip_address" : None,
                "adapter_addresses_by_type" : {
                    # "J2735-BSM" : [
                    #     # "192.168.2.6:39957",  # test 1-2
                    #     # "192.168.2.6:40079"   # test 3
                    # ],
                },
                "export_success" : True,
            }
        
        if  (   not "lvc" in this_site_metadata or 
                not "is_v2xhub" in this_site_metadata or 
                this_site_metadata["lvc"] == None or 
                this_site_metadata["is_v2xhub"] == None
            ) :

            site_type = get_site_type()

            if site_type == "v2xhub":
                site_lvc = "live"
                site_is_v2xhub = True
            else:
                site_lvc = site_type
                site_is_v2xhub = False
            
            this_site_metadata["lvc"] = site_lvc
            this_site_metadata["is_v2xhub"] = site_is_v2xhub

        if not "tdcs_dir" in this_site_metadata or this_site_metadata["tdcs_dir"] == None:
            this_site_metadata["tdcs_dir"] = os.path.join(site_dir_abs, "exported_tdcs")

        if not "ip_address" in this_site_metadata or this_site_metadata["ip_address"] == None:
            this_site_metadata["ip_address"] = input("\nEnter this site's IP address [xxx.xxx.xxx]: ")

        
        

        skip_export = create_folder(site_dir_abs,"exported_tdcs")
        if not skip_export:
            tdcs_file_path = find_largest_sqlite_file(site_dir_abs)
            os.chdir(site_dir_abs)
            try:
                tdcs_cmd = dataview_dir + " -d " + tdcs_file_path
                subprocess.run(tdcs_cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"\nError loading TDCS: \n{e}")
                this_site_metadata["export_success"] = False
            except Exception as e:
                print(f"\nError loading TDCS: \n{e}")
                this_site_metadata["export_success"] = False

        if not "adapter_addresses_by_type" in this_site_metadata or this_site_metadata["adapter_addresses_by_type"] == {}:
            this_site_metadata["adapter_addresses_by_type"] = get_adapter_addresses_by_type(this_site_metadata["tdcs_dir"],this_site_metadata["ip_address"])

        metatada.append(this_site_metadata)
        

    os.chdir(chosen_log_dir)
    with open('metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metatada, f, ensure_ascii=False, indent=4)
    
    print("\nFINISHED EXPORTING AND DECODING ALL DATA")


if __name__ == "__main__":
    main()


