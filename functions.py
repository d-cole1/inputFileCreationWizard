import csv
from datetime import datetime
import os


def main_func(window, values):
    if not validate_inputs(window, values):
        return

    max_data, min_data = get_csv_data(filepath=values['inp1'])

    output_max = generate_save_directory(csv_path=values['inp1'], sub_dir="MAX")
    output_min = generate_save_directory(csv_path=values['inp1'], sub_dir="MIN")

    write_to_file(dict_arg=max_data, save_dir=output_max, values=values, min_or_max="MAX")
    write_to_file(dict_arg=min_data, save_dir=output_min, values=values, min_or_max="MIN")

    window.write_event_value("Done", None)


def validate_inputs(window, values):
    input_file = values['inp1']
    user_mesh = values['mesh']
    user_bounds = values['bound_cond']

    if not input_file:
        window.write_event_value("Error", "no_file")
        return False

    if not user_mesh:
        window.write_event_value("Error", "no_input")
        return False

    if not user_bounds:
        window.write_event_value("Error", "no_bounds")
        return False

    return True


def get_csv_data(filepath):
    max_values = {}
    min_values = {}
    nodes_dofs = get_nodes_dofs(filepath)

    with open(filepath, 'r') as file:
        csv_reader = csv.reader(file)

        headers = next(csv_reader)  # Read first row

        point_index = headers.index("Point")  # Get index of "Point" header
        chan_number_index = headers.index("ChanNumber")  # Get index of "ChanNumber" header

        # Identify indices of headers containing "Chan" but not "ChanTitle" or "ChanNumber"
        chan_indices = []
        for index, header in enumerate(headers):
            if "Chan" in header and "ChanTitle" not in header and "ChanNumber" not in header:
                chan_indices.append(index)

        # Read each row after headers
        for row in csv_reader:
            chan_number = row[chan_number_index]  # Get value of "ChanNumber" for current row
            if chan_number not in max_values:
                max_values[chan_number] = []  # Create list for this ChanNumber if not already exist
            if chan_number not in min_values:
                min_values[chan_number] = []  # Create list for this ChaNumber if not already exist

            max_row_data = []
            min_row_data = []

            for i in chan_indices:
                if i < point_index:  # "Chan" headers before "Point" index
                    max_row_data.append(row[i])  # Store value in the max list
                else:  # "Chan" headers after "Point" index
                    min_row_data.append(row[i])  # Store value in the min list

                # Add min or max list to correct dictionary and key
                """max_values[chan_number] = (max_row_data)
                min_values[chan_number] = (min_row_data)"""

            zip_max = zip(nodes_dofs, max_row_data)
            zip_max_str = [f"{a},{b}" for a, b in zip_max]

            zip_min = zip(nodes_dofs, min_row_data)
            zip_min_str = [f"{c},{d}" for c, d in zip_min]

            max_values[chan_number] = (zip_max_str)
            min_values[chan_number] = (zip_min_str)

    return max_values, min_values


def get_nodes_dofs(file_path):
    results = []

    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames

        # Identify relevant headers
        chan_headers = [header for header in headers if "Chan" in header and header != "ChanTitle"]

        for row in reader:
            chan_number = row["ChanNumber"]
            node_id = row["NODE_ID"]
            dof = row["DOF"]

            # Check if ChanNumber is present in any of the Chan headers
            if any(row[header] == chan_number for header in chan_headers):
                result_string = f"{node_id},{dof}"
                results.append(result_string)

    return results


def generate_save_directory(csv_path, sub_dir):
    # Extract the directory from the provided CSV file path
    csv_dir = os.path.dirname(csv_path)

    # Get the current date in the desired format
    now = datetime.now()
    current_date = now.strftime("%d%b%y")

    # Create the output directory path
    output_dir = os.path.join(csv_dir, f"AbaqusWizardOutput_{current_date}")

    # Create the main output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create the subdirectory inside the main output directory
    sub_dir_path = os.path.join(output_dir, sub_dir)
    os.makedirs(sub_dir_path, exist_ok=True)

    return sub_dir_path


def write_to_file(save_dir, values, dict_arg, min_or_max):
    user_mesh = values['mesh']
    user_bounds = values['bound_cond'].splitlines()


    header1 = [
        "**",
        f"*INCLUDE, INPUT={user_mesh}"
    ]

    header2 = [
        "**",
        "**HMNAME LOADSTEP          1 HM_Step_1",
        "*STEP, AMPLITUDE = RAMP, INC =         1000, NLGEOM = YES",
        "Loading",
        "*STATIC",
        "0.1       ,1.0       ,1.0000E-05,1.0",
        "**HWNAME LOADCOL          1 HM_Load_Cols_1",
        "**HWCOLOR LOADCOL          1     3",
        "*BOUNDARY, OP=NEW"
    ]

    footer = [
        "**",
        "*OUTPUT, FIELD, FREQUENCY = 999",
        "*NODE OUTPUT",
        "U,",
        "*ELEMENT OUTPUT, POSITION = CENTROIDAL",
        "PEEQ,S",
        "*END STEP",
        "*****"
    ]
    for key, items in dict_arg.items():
        filename = os.path.join(save_dir, f"Strength_from_rsp_{min_or_max}_CHANNEL_{key}.inp")

        with open(filename, 'w') as file:
            for line in header1:
                file.write(line + '\n')

            for line in header2:
                file.write(line + "\n")

            for line in user_bounds:
                file.write(line.replace(" ", "") + '\n')

            file.write("*CLOAD, OP=NEW\n")

            for item in items:
                file.write(item + '\n')

            for line in footer:
                file.write(line + '\n')
