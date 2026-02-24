import ctypes
import os
from PIL import Image
import piexif
from datetime import datetime
import shutil
from time import sleep

#To copy from a drive it must have a file named "allow_copy" in the root directory 

#Change this field to change where the images are copied to
#Say you want it to be on a folder on your desktop you'd do "C:/Users/YOURUSERNAME/Desktop/Images"
#Note - if you are using onedrive to backup desktop it'd be "C:/Users/YOURUSERNAME/OneDrive/Desktop/Images"
save_location = "C:/CanonImages/"
allowed_Extenions = ["png","mp4","mov","jpg","jpeg","cr2","cr3"] #If not empty it'll only copy the specified file extentions (not case sensitive)

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

def extract_files(extractionDrive, location,allowedExt = [], forceExtraction = False):
    #create folder to store images
    os.makedirs(location, exist_ok=True)
    os.makedirs(location+ r"\.temp", exist_ok=True)

    if os.name == "nt":
        ctypes.windll.kernel32.SetFileAttributesW(location+ r"\.temp", 0x02) #set temp folder to be hidden          

    # get folders to extract from
    folders = os.listdir(os.path.join(extractionDrive[0],"DCIM"))

    #check for "allow_copy" file
    allow_copy = False
    for f in os.listdir(extractionDrive[0]):
        file,ext = os.path.splitext(f)
        if file == "allow_copy":
            allow_copy = True
            break

    if not allow_copy and not forceExtraction:
        print(f"NOTE: Drive label '{extractionDrive[1]}' Does not contain 'allow_copy' file, so will be skipped.")
        return

    #check drive for DCIM folder
    if os.path.isdir(os.path.join(extractionDrive[0],"DCIM")):
        print(f"NOTE: Drive label '{extractionDrive[1]}' Contains DCIM folder - Starting extraction")
    else:
        print(f"NOTE: Drive label '{extractionDrive[1]}' Does not contain DCIM folder - skipping")
        return
    
    # loop through each folder and copy files to C:\users\$user
    print("Starting file transer process...")
    for folder in folders:
        print("\n\nCopying files from: " + folder + "...")
        folderDirectory = os.path.join(extractionDrive[0],"DCIM",folder)
        files = os.listdir(folderDirectory)
        for file in files:
            fileDirectory = os.path.join(folderDirectory,file)

            if allowedExt != []:
                fileExtention = get_file_extention(fileDirectory)
                isAllowedExt  = False
                for ext in allowedExt:
                    if ext == fileExtention:
                        isAllowedExt = True
            else:
                isAllowedExt = True

            if os.path.isfile(fileDirectory) and isAllowedExt:
                if os.name == "nt": #windows
                    os.system(f'copy "{fileDirectory}" "{os.path.join(location,".temp")}"')
                else: #linux
                    os.system(f'cp "{fileDirectory}" "{os.path.join(location,".temp")}"')
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

def sort_images(location):
    tempImagePath = os.path.join(location,".temp")
    images = os.listdir(tempImagePath)

    #loop through each image and move it to a folder with a name corresponding to it's date taken
    for image in images:
        date = get_date_taken(tempImagePath + "/" + image)
        date = date.strftime("%d-%m-%Y")

        # make folder with name of date and move image to that folder
        if os.path.isdir(location + str(date)) == False:
            os.mkdir(location + str(date))
            print("Creating directory'" + location + str(date) + "'")
        
        if os.path.isfile(os.path.join(location,str(date),image)) == False:
            shutil.move(tempImagePath + "/" + image, location + str(date))
            print("Copied file '" + image + "' to " + os.path.join(location,str(date)))
        else:
            print("File '" + image + "' already exists in " + os.path.join(location,str(date)))

def get_file_extention(filePath):
    reversedExt = ""
    dotFound = False
    for i in range(len(filePath) -1,-1,-1):
        if filePath[i] != ".":
            reversedExt += filePath[i].lower()
        else:
            dotFound = True
            break
    if not dotFound:
        return False # return false because file has no "." so has no ext
    
    ext = reversedExt[::-1]
    return ext

if __name__ == "__main__":

    All_drives = get_external_drives()
    #loop through all drives and try to extract from it
    for drive in All_drives:
        extract_files(drive,save_location,allowed_Extenions)
    sort_images(save_location)
    print("Done")
    sleep(5)