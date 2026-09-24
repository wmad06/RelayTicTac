from pathlib import Path
import subprocess
import re
import tempfile
import time
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

# config variables
DEFAULT_FPS = 60
# manually select input and output folders
MANUAL_ENTRY = False
INPUT_FOLDER = Path(r"")
OUTPUT_FOLDER = Path(r"")
TIME_LOG_FILE = Path(__file__).parent / "time_log.txt"

# end config variables
# functions

def select_folders(): # uses file explorer GUI to select input and output folders.
    root = tk.Tk()
    root.withdraw()

    input_folder = filedialog.askopenfilename(
        title = "select ONE .png file in the input folder",
        initialdir=Path(__file__).parent,
        filetypes=[("PNG image", "*.png")]
    )
    if not input_folder:
        root.destroy()
        return None, None
    
    input_folder = Path(input_folder).parent

    

    output_folder = filedialog.askdirectory(
        title= "Select MP4 output folder",
        initialdir=Path(__file__).parent
    )

    if not output_folder:
        root.destroy()
        return None, None
    root.destroy()

    return input_folder, Path(output_folder)

def get_sort_key(path):
    return[
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]

def get_png_files(folder):
    return sorted(
        folder.glob("*.png"),
        key = get_sort_key
    )

def make_video(images, output_file, fps):
    frame_duration = 1 / fps

    with tempfile.NamedTemporaryFile(
        mode = "w",
        suffix =".txt",
        delete = False,
        encoding = "utf-8"
    ) as file_list:
        file_list_path = Path(file_list.name)

        for image in images:
            path = image.resolve().as_posix()

            file_list.write(f"file '{path}'\n")
            file_list.write(f"duration {frame_duration}\n")
        last_path = images[-1].resolve().as_posix()
        file_list.write(f"file '{last_path}'\n") 

    command = [
        "ffmpeg",
        "-y",

        "-f", "concat",
        "-safe", "0",
        "-i", str(file_list_path),

        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "medium",

        "-pix_fmt", "yuv420p",
        '-vf', "scale=trunc(iw/2)*2:trunc(ih/2)*2",

        "-movflags", "+faststart",

        str(output_file)
    ]

    try:
        subprocess.run(command, check=True)

    finally:
        file_list_path.unlink(missing_ok=True)

def get_camera_suffix_and_name(path):
    suffix = re.search(r"\.(\d+)$", path.stem)
    if suffix:
        cameraSuffix = suffix.group(1)
    else:
        cameraSuffix = ""
    name = path.stem
    name = name.removesuffix(f".{cameraSuffix}")
    name = re.sub(r"\d+$", "", name)
    return name, cameraSuffix

# end functions



def main():
    if not MANUAL_ENTRY:
        input_folder, output_folder = select_folders()
        if input_folder is None or output_folder is None:
            print("Error: Folder selection cancel")
            return
    else:
        input_folder = INPUT_FOLDER
        output_folder = OUTPUT_FOLDER

    start_time = time.perf_counter()
    start_date_time = datetime.now()
    videoCount = 0
    stoppedByUser = False

    if not input_folder.exists():
        print("ERROR: Input folder does not exist.")
        return

    images = get_png_files(input_folder)
    if not images:
        print("ERROR: no PNG files found.")
        return

    # names = []
    # suffixes_for_names = []
    # filteredImages = []

    # if she works she works
    image_dict = {}
    for image in images:
        name, suffix = get_camera_suffix_and_name(image)
            
        # beautiful dict code
        image_dict.setdefault(name,{})
        image_dict[name].setdefault(suffix,[])
        image_dict[name][suffix].append(image)

        # optional silly sausage conversion
    names = list(image_dict)
    suffixes_for_names = [list(image_dict[name]) for name in names]
    filteredImages = [list(name_dict.values()) for name_dict in image_dict.values()]
    
    # for image in images:
    #     name, suffix = get_camera_suffix_and_name(image)
    #     if not name in names:
    #         names.append(name)
    #         filteredImages.append([[image]])
    #         nameIndex = names.index(name)
    #         suffixes_for_names.append([suffix])
    #     else:
    #         nameIndex = names.index(name)
    #         if not suffix in suffixes_for_names[nameIndex]:
    #             suffixes_for_names[nameIndex].append(suffix)
    #             filteredImages[nameIndex].append([image])
    #         else:
    #             suffixIndex = suffixes_for_names[nameIndex].index(suffix)
    #             filteredImages[nameIndex][suffixIndex].append(image)
    currentName = ""
    currentSuffix = ""
    try:                
        for i in range(len(filteredImages)):
            currentName = names[i]
            suffixCount = len(suffixes_for_names[i])
            if (currentName == ""):
                print(f"\nCreating videos for empty name. With {suffixCount} suffixes.\n")
            else: 
                print(f"\nCreating videos for name: {currentName}. With {suffixCount} suffixes.\n")
            for j in range(len(filteredImages[i])):
                currentSuffix = suffixes_for_names[i][j]
                if currentName == "" and currentSuffix == "":
                    outputFile = output_folder / f"Bro, why didn't you name your render outputs.mp4"
                elif currentName == "":
                    outputFile = output_folder / f"{currentSuffix}.mp4"
                elif currentSuffix == "":
                    outputFile = output_folder / f"{currentName}.mp4"
                else:
                    outputFile = output_folder / f"{currentName}_{currentSuffix}.mp4"
                if (currentName == ""):
                    if currentSuffix == "":
                        print("\nCreating video for empty name, empty suffix\n")
                    else:
                        print("\nCreating video for empty name, suffix:", currentSuffix, "\n")
                else:
                    if currentSuffix == "":
                        print("\nCreating video for name:", currentName, ", empty suffix\n")
                    else:
                        print("\nCreating video for name:", currentName, ", suffix:", currentSuffix, "\n")
                make_video(filteredImages[i][j], outputFile,DEFAULT_FPS)
                videoCount += 1
                if (currentName == ""):
                    if currentSuffix == "":
                        print("\nFinished creating video for empty name, empty suffix\n")
                    else:
                        print("\nFinished creating video for empty name, suffix:", currentSuffix, "\n")
                else:
                    if currentSuffix == "":
                        print("\nFinished creating video for name:", currentName, ", empty suffix\n")
                    else:
                        print("\nFinished creating video for name:", currentName, ", suffix:", currentSuffix, "\n")
                print(f"Video count: {videoCount}")
    except KeyboardInterrupt:
        print("\nGeneration stopped by user!")
        print(f"Total full videos completed successfully: {videoCount}")
        print("!!!This may cause a partially stitched video!!!\nCheck log to find file that may be affected")
        stoppedByUser = True
    stopMessage = ""
    if stoppedByUser:
        if currentName == "":
            if  currentSuffix == "":
                stopMessage = f" | Generation stopped at empty name, empty suffix. This may cause a partially stitched video!"
            else:
                stopMessage = f" | Generation stopped at empty name, suffix: {currentSuffix}. This may cause a partially stitched video!"
        else:
            if currentSuffix == "":
                stopMessage = f" | Generation stopped at name: {currentName}, empty suffix. This may cause a partially stitched video!"
            else:
                stopMessage = f" | Generation stopped at name: {currentName}, suffix: {currentSuffix}. This may cause a partially stitched video!"

    status = "STOPPED BY USER" if stoppedByUser else "COMPLETED"
    end_time = time.perf_counter()
    end_date_time = datetime.now()

    total_time = end_time - start_time
    hours = int(total_time//3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)
    elapsedString = f"Elapsed time (HH:mm:ss): {hours:02}:{minutes:02}:{seconds:02}"
    print(elapsedString)

    with open(TIME_LOG_FILE, "a",
              encoding = "utf-8") as file:
        file.write(
            f"Status: {status} | "
            f"Videos generated: {videoCount} | "
            f"Start: {start_date_time:%Y-%m-%d %H:%M:%S} | "
            f"End: {end_date_time:%Y-%m-%d %H:%M:%S} | "
            f"{elapsedString}"
            f"{stopMessage}\n"

        )
    if not stoppedByUser:
        print("ALL DONE!")


if __name__ == "__main__":
    main()

