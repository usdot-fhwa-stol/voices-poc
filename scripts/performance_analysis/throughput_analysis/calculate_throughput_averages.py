import sys
import re
import csv
import argparse


## This script is used to convert nethogs text output to csv format
## It takes an input of a text file of nethogs output
## The csv produced will contain a column for each application that appears in the text file
## A row will be added for every time step
##
## Example collection command:
##
##     sudo nethogs -d 1 -t > run_7_aug_all.txt
##
## Example script usage:
##
##     python3 calculate_throughput_averages.py -i run_7_mitre_all.txt -o run_7_mitre_all_output.csv
##

argparser = argparse.ArgumentParser(
    description='Calculate network throughput from nethogs output')

argparser.add_argument(
    '-i', '--infile',
    metavar='<infile>',
    dest='infile',
    type=str,
    default=None,
    help='name of the infile (no special characters or spaces)')
argparser.add_argument(
    '-o', '--outfile',
    metavar='<outfile>',
    dest='outfile',
    type=str,
    default=None,
    help='name of the outfile (no special characters or spaces)')
args = argparser.parse_args()

if args.infile == None:
    print("\nERROR - NO INFILE SPECIFIED\n")
    print(argparser.print_help())
    sys.exit()
else:
    infile = str(args.infile)
    infile_obj = open(infile,'r')

refresh_index = 0

outfile = args.outfile

if args.outfile == None:
    print("\nERROR - NO OUTFILE SPECIFIED\n")
    print(argparser.print_help())
    sys.exit()
else:
    outfile = str(args.outfile)
    results_outfile_obj = open(outfile,'w',newline='')
    results_outfile_writer = csv.writer(results_outfile_obj)



results_dataset = {}

for line_i,line in enumerate(infile_obj):
    current_line = line.strip()
    
    if "Adding local address" in current_line or "Ethernet link detected" in current_line:
        continue
    if current_line == "Refreshing:":
        refresh_index += 1
        continue
    elif current_line == "":
        continue
    else:
        # print(str(line_i) + " - " + str(refresh_index) + " - " + current_line)

        current_line_list = current_line.split("	")
        
        current_line_app = current_line_list[0]
        current_line_up = current_line_list[1]
        current_line_down = current_line_list[2]
        
        # print("\tApp: " + current_line_app)
        # print("\tUP: " + current_line_up)
        # print("\tDOWN: " + current_line_down)

        if not current_line_app in results_dataset:
            results_dataset[current_line_app] = {
                str(refresh_index) : {
                    "up" : current_line_up,
                    "down" : current_line_down 
                }
                
            }
        else:
            results_dataset[current_line_app][str(refresh_index)] = {}
            results_dataset[current_line_app][str(refresh_index)]["up"] = current_line_up
            results_dataset[current_line_app][str(refresh_index)]["down"] = current_line_down

# print(str(results_dataset))

header_row = []

for app in results_dataset:
    header_row.append(app + "_UP")
    header_row.append(app + "_DOWN")

results_outfile_writer.writerow(header_row)

for this_refresh_index in range(1,refresh_index):
    # print("\nWriting refresh: " + str(this_refresh_index))

    row_to_write = []

    for app in results_dataset:
        # print("  Checking app for data: " + app)
        if str(this_refresh_index) in results_dataset[app]:
            # print("    UP: " + results_dataset[app][str(this_refresh_index)]["up"])
            # print("    DOWN: " + results_dataset[app][str(this_refresh_index)]["down"])

            row_to_write.append(results_dataset[app][str(this_refresh_index)]["up"])
            row_to_write.append(results_dataset[app][str(this_refresh_index)]["down"])

        else:
            # print("    UP: NO DATA" )
            # print("    DOWN: NO DATA")

            row_to_write.append("NO DATA")
            row_to_write.append("NO DATA")
    
    results_outfile_writer.writerow(row_to_write)






