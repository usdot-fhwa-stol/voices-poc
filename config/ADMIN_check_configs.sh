#!/bin/bash

# set -e

# Set the path to the site_config folder
site_config_folder="./site_config"

# Find the default_site.config file
default_config="$site_config_folder/default_site.config"

# Check if default_site.config exists
if [ -e "$default_config" ]; then
    # Loop through all .config files in the site_config folder
    for config_file in "$site_config_folder"/*.config; do
        # Skip the default_site.config file itself
        if [ "$config_file" != "$default_config" ]; then
            # Compare files and print differences

            config_file_basename=$(basename $config_file)

            echo
            echo 'Comparing: '$config_file_basename

            # other file must have new line at end of file, add it if it doesnt exist
            # this part removes all newlines
            while [[ -s "$config_file" && -z "$(tail -c 1 "$config_file")" ]]; do
                truncate -s -1 $config_file
                other_last_char=$(tail -c 1 "$config_file")
            done

            # this one adds one back
            sed -i -e '$a\' $config_file            

            default_line_count=$(wc -l < "$default_config")
            other_line_count=$(wc -l < "$config_file")

            echo
            echo "default_site.config lines: "$default_line_count
            echo $config_file_basename "lines: "$other_line_count

            # Find the maximum
            if [ "$default_line_count" -gt "$other_line_count" ]; then
                max_line_count="$default_line_count"
            else
                max_line_count="$other_line_count"
            fi

            mapfile -t default_lines < "$default_config"
            mapfile -t other_lines < "$config_file"

            echo 

            default_config_line_offset=0
            other_config_line_offset=0
            num_lines_inserted=0

            line_index=0
            while (( $line_index <= max_line_count )); do
                echo Checking Line: $((line_index + 1))

                mapfile -t default_lines < "$default_config"
                mapfile -t other_lines < "$config_file"

                default_line_count=$(wc -l < "$default_config")
                other_line_count=$(wc -l < "$config_file")

                # Find the maximum
                if [ "$default_line_count" -gt "$other_line_count" ]; then
                    max_line_count="$default_line_count"
                else
                    max_line_count="$other_line_count"
                fi


                default_index=$((line_index + default_config_line_offset))
                other_index=$((line_index + other_config_line_offset))

                default_line=${default_lines[default_index]}
                other_line=${other_lines[other_index]}

                if [[ $default_line != $other_line ]]; then

                    if [[ $default_line == "#"* ]] || [[ $default_line == "" ]]; then
                        stripped_default_line=$default_line
                        stripped_other_line=$other_line
                    else
                        stripped_default_line=$(echo $default_line | grep -oP "export \K.*(?==)")
                        stripped_other_line=$(echo $other_line | grep -oP "export \K.*(?==)")
                    fi

                    echo $'\t[XXX] Config Lines do not Match: '

                    echo $'\t\tDefault Line '"$((default_index + 1)): $default_line"
                    echo $'\t\tOther Line '"$((other_index + 1)): $other_line"
                    # echo $'\t\tStripped Default Line '"$((default_index + 1)): $stripped_default_line"
                    # echo $'\t\tStripped Other Line '"$((other_index + 1)): $stripped_other_line"

                    if [[ $stripped_default_line == $stripped_other_line ]]; then
                        echo $'\t\t[~~~] Default and other have same config param but different values'
                        ((line_index+=1))
                        continue
                    fi

                    # Check if the param exists in the other file but on a different line
                    # if it does, move on, if it doesnt, we need to add it
                    prev_other_line=${other_lines[other_index -1]}

                    echo other_line_count: $other_line_count

                    if [[ $((other_index +1)) -lt $other_line_count ]] && [[ $other_line == "" ]]; then
                        echo $'\t\t'"[---] Double newline was found in '$config_file', removing one."
                        other_index_d=$((other_index + 1))"d"
                        sed -i $other_index_d $config_file
                        continue
                    fi

                    if [[ $default_line == "" ]]; then
                        echo $'\t\t'"[+++] Inserting newline from default into file"
                        insert_index=$((other_index + 1 + num_lines_inserted))
                        sed -i "${insert_index}  i\\"$'\n'"" $config_file
                        continue
                    fi

                    matching_line_in_other=$(grep "$stripped_default_line" "$config_file")

                    if [ -n "$matching_line_in_other" ]; then
                        echo $'\t\t'"The param '$stripped_default_line' was found in '$config_file' on a different line."
                        # echo $'\t\t'"Matching line: $matching_line_in_other"
                        
                        matching_line_in_default=$(grep "$stripped_other_line" "$default_config")

                        if [ ! -n "$matching_line_in_default" ]; then
                            echo $'\t\t'"[---] The param '$stripped_other_line' was found in '$config_file' but not in default, removing it."
                            other_index_d=$((other_index + 1 + num_lines_inserted))"d"
                            sed -i $other_index_d $config_file
                            # echo $'\t\t'"Matching line: $matching_line_in_other"
                        fi
                    else
                        echo $'\t\t'"The param '$stripped_default_line' exists in the default but was not found in '$config_file'."
                        
                        # to get the line into the same place as the default, 
                        # we need to add the other_index, 
                        # plus 1 to get to the line below
                        # plus however many lines we added above it
                        insert_index=$((other_index + 1 + num_lines_inserted))
                        
                        # get a new line count to see if we are past the end of the other file
                        other_line_count=$(wc -l < "$config_file")

                        if [[ $insert_index -gt $other_line_count ]]; then
                            
                            echo $'\t\t'"[+++] Adding line from default to end of file"

                            prev_default_line=${default_lines[default_index -1]}

                            if [[ $prev_default_line == "" ]]; then

                                echo $'\n'$default_line >> $config_file
                            else
                                echo $default_line >> $config_file
                            fi

                        else
                            echo $'\t\t'"[+++] Inserting line from default into file"
                            sed -i "$insert_index i $default_line" $config_file
                        fi                        
                    fi
                else
                        echo $'\t[OOO] Config Lines Match: '$default_line
                        ((line_index+=1))
                fi

            done
        fi
    done
else
    echo "Error: default_site.config not found in $site_config_folder."
fi

echo
echo "FINSHED CHECKING CONFIG"