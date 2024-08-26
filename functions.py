import csv
from datetime import datetime
import os


def main_func(window, values):
    if not validate_inputs(window, values):
        return

    max_data, min_data = get_csv_data(filepath=values['inp1'])

    output_max = generate_save_directory(csv_path=values['inp1'], sub_dir="MAX", mesh_name=values['mesh'])
    output_min = generate_save_directory(csv_path=values['inp1'], sub_dir="MIN", mesh_name=values['mesh'])

    write_to_file(dict_arg=max_data, save_dir=output_max, values=values, min_or_max="MAX")
    write_to_file(dict_arg=min_data, save_dir=output_min, values=values, min_or_max="MIN")

    window.write_event_value("Done", None)


def validate_inputs(window, values):
    input_file = values['inp1']
    user_mesh = values['mesh']
    user_bounds = values['bound_cond']

    if not input_file:
        window.write_event_value("Error", "no_csv")
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
        headers = next(csv_reader)  # Read first row which contains headers

        # Get index of "Point" and "ChanNumber" headers
        point_index = headers.index("Point")
        chan_number_index = headers.index("ChanNumber")

        # Identify indices of headers containing "Chan" but not "ChanTitle" or "ChanNumber"
        chan_indices = []
        for index, header in enumerate(headers):
            if "Chan" in header and "ChanTitle" not in header and "ChanNumber" not in header:
                chan_indices.append(index)

        # Read each row after headers
        for row in csv_reader:
            chan_number = row[chan_number_index]  # Get value of "ChanNumber" for current row

            # Only process if ChanNumber in headers
            if f"Chan{chan_number}" in headers:

                # Create list for this ChanNumber if not already exists
                if chan_number not in max_values:
                    max_values[chan_number] = []
                if chan_number not in min_values:
                    min_values[chan_number] = []

                max_row_data = []
                min_row_data = []

                # Separate data into max and min lists based on position of "Chan" headers
                for i in chan_indices:
                    if i < point_index:
                        max_row_data.append(row[i])  # Store value in the max list
                    else:
                        min_row_data.append(row[i])  # Store value in the min list

                # Pair nodes-dofs with max data and min data
                zip_max = zip(nodes_dofs, max_row_data)
                zip_max_str = [f"{a},{b}" for a, b in zip_max]

                zip_min = zip(nodes_dofs, min_row_data)
                zip_min_str = [f"{c},{d}" for c, d in zip_min]

                # Store the paired data in the dictionaries
                max_values[chan_number] = zip_max_str
                min_values[chan_number] = zip_min_str

    return max_values, min_values


def get_nodes_dofs(file_path):
    unique_pairs = []

    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames

        chan_headers = []
        for header in headers:
            if "Chan" in header and "ChanTitle" not in header:
                chan_headers.append(header)

        for row in reader:
            chan_number = row["ChanNumber"]  # Get value of ChanNumber for current row
            node_id = row["NODE_ID"]  # Get value of NODE_ID for current row
            dof = row["DOF"]  # Get value of DOF for current row

            # Only add unique node_id,dof pairs for each ChanNumber
            if f"Chan{chan_number}" in chan_headers:
                unique_pair = f"{node_id},{dof}"
                if unique_pair not in unique_pairs:
                    unique_pairs.append(unique_pair)

    return unique_pairs


def generate_save_directory(csv_path, sub_dir, mesh_name):
    # Extract the directory from the provided CSV file path
    csv_dir = os.path.dirname(csv_path)

    # Get the current date in the desired format
    now = datetime.now()
    current_date = now.strftime("%d%b%y")

    # Create the output directory path
    output_dir = os.path.join(csv_dir, f"AbaqusWizardOutput({mesh_name.strip('.inp')})_{current_date}")

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
