import ctypes
import os
from PIL import Image
import piexif
import os
from datetime import datetime
import shutil
from time import sleep


save_location = "C:/CanonImages/"

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

def extract_files(extractionDrive):
    #create folder to store images
    imageFolder = save_location
    os.makedirs(imageFolder, exist_ok=True)
    os.makedirs(imageFolder+ r"\temp", exist_ok=True)
    ctypes.windll.kernel32.SetFileAttributesW(imageFolder+ r"\temp", 0x02)
    print(f"Directory at: {imageFolder}")
    #check drive for DCIM folder
    if os.path.isdir(os.path.join(extractionDrive[0],"DCIM")):
        print(f"NOTE: Drive {extractionDrive[1]} Contains DCIM folder - Starting extraction")
    else:
        print(f"NOTE: Drive {extractionDrive[1]} Does not contain DCIM folder - skipping")
            

    # get folders to extract from
    folders = os.listdir(os.path.join(extractionDrive[0],"DCIM"))
    
    # loop through each folder and copy files to C:\users\$user
    print("Starting file transer process...")
    for folder in folders:
        print("\n\nCopying files from: " + folder + "...")
        os.system("robocopy " + extractionDrive[0] + "DCIM/" + folder + " " + imageFolder + "/temp" + r' *.* /S /E /DCOPY:DA /COPY:DAT /R:1000000 /W:30 | findstr /V /C:"ROBOCOPY" /C:"Started :" /C:"Source =" /C:"Dest :" /C:"Files :" /C:"Options :" /C:"------------------------------------------------------------------------------"')
    print("File transfer finished.")

def get_date_taken(path):
    try:
        with Image.open(path) as img:
            if "exif" in img.info:
                exif_data = piexif.load(img.info["exif"])
                date_taken_bytes = exif_data["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
                if date_taken_bytes:
                    date_taken_str = date_taken_bytes.decode("utf-8")
                    return datetime.strptime(date_taken_str, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"EXIF read error: {e}")

    # Fallback: use file's modification time
    try:
        stat = os.stat(path)
        return datetime.fromtimestamp(stat.st_mtime)
    except Exception as e:
        print(f"File access error: {e}")
        return None

def sort_images():
    tempImagePath = os.path.join(save_location,"temp")
    images = os.listdir(tempImagePath)

    #loop through each image and move it to a folder with a name corresponding to it's date taken
    for image in images:
        date = get_date_taken(tempImagePath + "/" + image)
        date = date.strftime("%d-%m-%Y")

        # make folder with name of date and move image to that folder
        if os.path.isdir(save_location + str(date)) == False:
            os.mkdir(save_location + str(date))
            print("Creating directory'" + save_location + str(date) + "'")
        
        if os.path.isfile(os.path.join(save_location,str(date),image)) == False:
            shutil.move(tempImagePath + "/" + image, save_location + str(date))
            print("Copied file '" + image + "' to " + os.path.join(save_location,str(date)))
        else:
            print("File '" + image + "' already exists in " + os.path.join(save_location,str(date)))

if __name__ == "__main__":

    All_drives = get_external_drives()
    #loop through all drives and try to extract from it
    for drive in All_drives:
        extract_files(drive)
    sort_images()
    print("Done")
    sleep(5)