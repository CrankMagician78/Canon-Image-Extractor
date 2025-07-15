import ctypes
import string
import os
from PIL import Image
import piexif
import os
from datetime import datetime

def get_external_drives():
    drives = []
    drive_bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for i in range(26):
        if drive_bitmask & (1 << i):
            drive_letter = f"{chr(65 + i)}:\\"
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(drive_letter))
            if drive_type == 2:
                volume_name = ctypes.create_unicode_buffer(1024)
                fs_name = ctypes.create_unicode_buffer(1024)
                serial_number = ctypes.c_ulong()
                max_component_len = ctypes.c_ulong()
                file_system_flags = ctypes.c_ulong()

                ctypes.windll.kernel32.GetVolumeInformationW(
                    ctypes.c_wchar_p(drive_letter),
                    volume_name,
                    ctypes.sizeof(volume_name),
                    ctypes.byref(serial_number),
                    ctypes.byref(max_component_len),
                    ctypes.byref(file_system_flags),
                    fs_name,
                    ctypes.sizeof(fs_name)
                )
                drives.append((drive_letter, volume_name.value))
    return drives

def select_external_drive():
    drives = get_external_drives()
    if not drives:
        print("No external (removable) drives found.")
        return None

    print("External drives detected:")
    for idx, (letter, label) in enumerate(drives, 1):
        print(f"{idx}: {letter} - {label or 'No Label'}")

    while True:
        selected_drive = ""
        try:
            choice = int(input("Select a drive by number: "))
            if 1 <= choice <= len(drives):
                selected_drive = drives[choice - 1][0]
        except ValueError:
            selected_drive = ""
            pass

        if selected_drive != "":
            os.chdir(selected_drive)
            if os.path.isdir("DCIM"):
                print(f"You selected: {selected_drive}")
                return selected_drive
            else:
                selected_drive = ""
                print("invalid selection. No DCIM folder present. Please try again.")
        else:
            print("Invalid selection. Please try again.")


def extract_files(extractionDrive):
    #create folder to store images
    imageFolder = os.path.expanduser("~")+ r"\OneDrive\Pictures\CanonImages"
    os.makedirs(imageFolder, exist_ok=True)
    os.makedirs(imageFolder + r"\Unsorted", exist_ok=True)
    os.makedirs(imageFolder+ r"\temp", exist_ok=True)
    ctypes.windll.kernel32.SetFileAttributesW(imageFolder+ r"\temp", 0x02)
    print(f"Directory at: {imageFolder}")

    # get folders to extract from
    os.chdir("DCIM")
    folders = os.listdir()
    extractionFolders = []
    for i in folders:
       if i.endswith("CANON"):
           extractionFolders.append(i)
    
    # loop through each folder and copy files to C:\users\$user
    print("Starting file transer process...")
    for folder in extractionFolders:
        print("\n\nCopying files from: " + folder)
        os.system("robocopy " + extractionDrive + "DCIM/" + folder + " " + imageFolder + "/temp" + r' *.* /S /E /DCOPY:DA /COPY:DAT /R:1000000 /W:30 | findstr /V /C:"ROBOCOPY" /C:"Started :" /C:"Source =" /C:"Dest :" /C:"Files :" /C:"Options :" /C:"------------------------------------------------------------------------------"')
    print("File transfer finished.")

def sort_images():
    tempImagePath = os.path.expanduser("~")+ r"\OneDrive\Pictures\CanonImages\temp"
    images = os.listdir(tempImagePath)
    print(images)

    #loop through each image and move it to a folder with a name corresponding to it's date taken
    for image in images:
        print()
if __name__ == "__main__":
    print("Welcome to the Canon Image Extractor")
    selected = select_external_drive()
    extract_files(selected)
    sort_images()

