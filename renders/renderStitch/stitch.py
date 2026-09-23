from pathlib import Path
import subprocess
import re
import tempfile
import time
from datetime import datetime

# config variables
DEFAULT_FPS = 60
INPUT_FOLDER = Path(r"C:\Users\Will\Documents\.projects\RelayTicTac\test stitch\pngs\mega")
OUTPUT_FOLDER = Path(r"C:\Users\Will\Documents\.projects\RelayTicTac\test stitch\vidout\megaOut")
TIME_LOG_FILE = Path(r"C:\Users\Will\Documents\.projects\RelayTicTac\gitMonster\RelayTicTac\renders\renderStitch\time_log.txt")

# end config variables
# functions
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
    start_time = time.perf_counter()
    start_date_time = datetime.now()

    if not INPUT_FOLDER.exists():
        print("ERROR: Input folder does not exist.")
        return

    images = get_png_files(INPUT_FOLDER)
    if not images:
        print("ERROR: no PNG files found.")
        return

    names = []
    suffixes_for_names = []
    filteredImages = []

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
                
    for i in range(len(filteredImages)):
        if (names[i] == ""):
            print("\nCreating video for empty name\n")
        else: 
            print("\nCreating video for name: ", names[i], "\n")
        for j in range(len(filteredImages[i])):
            if names[i] == "" and suffixes_for_names[i][j] == "":
                outputFile = OUTPUT_FOLDER / f"bro, why didn't you name your outputs?.mp4"
            elif names[i] == "":
                outputFile = OUTPUT_FOLDER / f"{suffixes_for_names[i][j]}.mp4"
            elif suffixes_for_names[i][j] == "":
                outputFile = OUTPUT_FOLDER / f"{names[i]}.mp4"
            else:
                outputFile = OUTPUT_FOLDER / f"{names[i]}_{suffixes_for_names[i][j]}.mp4"
            if (names[i] == ""):
                if suffixes_for_names[i][j] == "":
                    print("\nCreating video for empty name, empty suffix\n")
                else:
                    print("\nCreating video for empty name, suffix:", suffixes_for_names[i][j], "\n")
            else:
                if suffixes_for_names[i][j] == "":
                    print("\nCreating video for name:", names[i], ", empty suffix\n")
                else:
                    print("\nCreating video for name:", names[i], ", suffix:", suffixes_for_names[i][j], "\n")
            make_video(filteredImages[i][j], outputFile,DEFAULT_FPS)
            if (names[i] == ""):
                if suffixes_for_names[i][j] == "":
                    print("\nFinished creating video for empty name, empty suffix\n")
                else:
                    print("\nFinished creating video for empty name, suffix:", suffixes_for_names[i][j], "\n")
            else:
                if suffixes_for_names[i][j] == "":
                    print("\nFinished creating video for name:", names[i], ", empty suffix\n")
                else:
                    print("\nFinished creating video for name:", names[i], ", suffix:", suffixes_for_names[i][j], "\n")
            
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
            f"Start: {start_date_time:%Y-%m-%d %H:%M:%S} | "
            f"End: {end_date_time:%Y-%m-%d %H:%M:%S} | "
            f"{elapsedString}\n"
        )
    print("ALL DONE!")


if __name__ == "__main__":
    main()

