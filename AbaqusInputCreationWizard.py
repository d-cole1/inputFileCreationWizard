import PySimpleGUI as sg
from functions import main_func

# Define a custom theme for the GUI
my_new_theme = {'BACKGROUND': "#31363b",
                'TEXT': "#f9f1ee",
                'INPUT': "#232629",
                'TEXT_INPUT': "#f9f1ee",
                'SCROLL': "#333a41",
                'BUTTON': ('#31363b', '#0dd1fc'),
                'PROGRESS': ('#f9f1ee', '#31363b'),
                'BORDER': 1,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0}

logo = r"C:\Users\dominick.cole\Python\inputCreationWizard\logos\abacus.ico"
e_logo = r"C:\Users\dominick.cole\Python\inputCreationWizard\logos\error.ico"
s_logo = r"C:\Users\dominick.cole\Python\inputCreationWizard\logos\success.ico"

# Add and set the custom theme
sg.theme_add_new("MyNewTheme", my_new_theme)
sg.theme("MyNewTheme")
sg.set_options(font=("Helvetica", 12))

layout = [
    [sg.Text("Add mesh input file name:", size=(20, 1), pad=(1, 15)),
     sg.InputText(key="mesh", size=(53, 1))],

    [sg.Text("Add boundary conditions below (one per line):", pad=(1, 5))],
    [sg.Multiline(key="bound_cond", autoscroll=True, size=(40, 10), pad=(1, 5))],

    [sg.Radio(".csv", "RADIO1", key='-CSV-', enable_events=True, pad=(1, 5)),
     sg.Radio(".rsp (in development)", "RADIO1", disabled=True, key='-RSP-', enable_events=True, pad=(1, 5))],

    [sg.pin(sg.Column([[sg.Text(key='inp1_txt', size=(14, 1)),
                        sg.Input(key="inp1", size=(49, 1)),
                        sg.FileBrowse("Choose", file_types=(("CSV file", "*.csv"),))]],
                                                key='csv_req', visible=False, pad=(0, 5)))],

    [sg.pin(sg.Column([[sg.Text(key='inp2_txt', size=(14, 1)),
                        sg.Input(key='inp2', size=(49, 1)),
                        sg.FileBrowse("Choose", file_types=(("RSP file", "*.rsp"),))]],
                                                key='rsp_req', visible=False, pad=(0, 5)))],

    [sg.Button("Create Input File", key="create", disabled=True)]
]

window = sg.Window('ABAQUS Input File Creation Wizard', layout=layout, icon=logo)

while True:
    event, values = window.read()

    match event:
        case sg.WIN_CLOSED:
            break

        case '-CSV-':
            window['csv_req'].update(visible=True)
            window['rsp_req'].update(visible=False)
            window['inp1_txt'].update('Select .csv file:')
            window['create'].update(disabled=False)

        case '-RSP-':
            window['csv_req'].update(visible=True)
            window['rsp_req'].update(visible=True)
            window['inp1_txt'].update('Select .rsp file:')
            window['inp2_txt'].update('Select mesh map:')
            window['create'].update(disabled=False)

        case 'create':
            main_func(window, values)

        case 'Done':
            sg.popup("An output folder has been created in the same folder as the .csv file you selected",
                     custom_text="Exit", icon=s_logo, title="SUCCESS!")
            break

        case 'Error':
            error_type = values[event]

            if error_type == 'no_csv':
                sg.popup('Ensure a .csv file is selected.', icon=e_logo, title="ERROR!")

            if error_type == 'no_input':
                sg.popup('Ensure a mesh name is entered.', icon=e_logo, title="ERROR!")

            if error_type == 'no_bounds':
                sg.popup('Ensure the boundary conditions are entered.', icon=e_logo, title="ERROR!")

window.close()
