import os
import subprocess
import PySimpleGUI as sg


def generate_requirements_txt():
    try:
        subprocess.check_call(
            ["pip", "freeze", ">", "requirements.txt"], shell=True
        )
        return True
    except Exception as e:
        return str(e)


def backup_packages(backup_dir, window):
    try:
        wheelhouse_dir = os.path.join(backup_dir, "wheelhouse")
        os.makedirs(wheelhouse_dir, exist_ok=True)
        process = subprocess.Popen(
            [
                "pip",
                "wheel",
                "--wheel-dir",
                wheelhouse_dir,
                "-r",
                "requirements.txt",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        for line in process.stdout:
            window["-OUTPUT-"].print(line)
            window["-PROGRESS-"].update_bar(1)
        return True
    except Exception as e:
        return str(e)


def download_packages(backup_dir, window):
    try:
        process = subprocess.Popen(
            ["pip", "download", "--dest", backup_dir, "-r", "requirements.txt"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        for line in process.stdout:
            window["-OUTPUT-"].print(line)
            window["-PROGRESS-"].update_bar(1)
        return True
    except Exception as e:
        return str(e)


def restore_packages(restore_dir):
    try:
        subprocess.check_call(
            [
                "pip",
                "install",
                "--no-index",
                "--find-links",
                os.path.join(restore_dir, "wheelhouse"),
                "-r",
                "requirements.txt",
            ]
        )
        return True
    except Exception as e:
        return str(e)


layout = [
    [
        sg.Text(
            "Python Package Backup/Restore Tool",
            size=(30, 1),
            font=("Helvetica", 14),
        )
    ],
    [
        sg.Text("Choose an action: "),
        sg.Radio("Backup", "RADIO1", key="-BACKUP-", default=True),
        sg.Radio("Restore", "RADIO1", key="-RESTORE-"),
    ],
    [
        sg.Text("Directory:"),
        sg.InputText(key="-DIR-"),
        sg.FolderBrowse(button_text="Browse"),
    ],
    [
        sg.Checkbox(
            "Download packages from the internet",
            key="-DOWNLOAD-",
            default=False,
        )
    ],
    [sg.ProgressBar(100, orientation="h", size=(20, 20), key="-PROGRESS-")],
    [sg.Output(size=(50, 10), key="-OUTPUT-")],
    [sg.Button("Execute"), sg.Button("Exit")],
]

window = sg.Window("Package Backup/Restore Tool", layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Exit":
        break
    elif event == "Execute":
        action = "backup" if values["-BACKUP-"] else "restore"
        directory = values["-DIR-"]
        if not directory:
            sg.popup_error("Please select a directory.")
        else:
            if action == "backup":
                window["-PROGRESS-"].update(0, 100)
                window["-OUTPUT-"].update("")  # Clear previous output
                if values["-DOWNLOAD-"]:
                    success = download_packages(directory, window)
                else:
                    success = generate_requirements_txt() and backup_packages(
                        directory, window
                    )
            else:
                success = restore_packages(directory)

            if success:
                sg.popup("Operation successful.")
            else:
                sg.popup_error(
                    "Operation failed. Check the console for details."
                )

window.close()
