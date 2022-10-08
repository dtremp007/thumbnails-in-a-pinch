#!/Users/david/opt/anaconda3/bin/python

import sys
from subprocess import run
from pathlib import Path
from re import compile
from PIL import Image

THUMBNAIL_SUFFIX = "_1280x720"
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720
NEW_DIRECTORY = f"thumbnail{THUMBNAIL_SUFFIX}"


def build_sort_machine(discard_pile: list[Path], work_queue: list[Path], options):
    """
    * `discard_pile`: a list for holding all the files that meet the discard_parameters, in case you want to do something with them.
    * `work_queue`: these are all the files that need work.
    * `options`: currently just consists of one field, `discard_parameters`: a list of functions that take a file and either return true or false.

    @returns a `sort()` function.
    """

    def sort(file: Path):
        shouldDiscard = 0

        for func in options["discard_parameters"]:
            if func(file):
                shouldDiscard += 1

        if shouldDiscard == 0:
            work_queue.append(file)
        else:
            discard_pile.append(file)

    return sort


def generate_file_paths(file: Path, target_dir: Path):
    """
    Takes the `Path` object of the current file and target dir. Appends `THUMBNAIL_SUFFIX` to end of new file.
    @returns a tuple with each path resolved as a string.
    """

    file_stem = file.stem
    file_suffix = file.suffix
    file_path = str(file.resolve())
    target_dir_path = str(target_dir.resolve())
    new_file_path = f"{target_dir_path}/{file_stem}{THUMBNAIL_SUFFIX}.jpeg"

    return (file_path, new_file_path)


def reduce_image(file: Path, current_path, target_path):
    """
    Uses `run()` from `subprocess` module to execute the `convert` command from ImageMagick.
    """
    try:
        with Image.open(current_path) as image:

            # RGBA mode can't be converted to JPEG, so I first had to convert it to RGB
            if file.suffix == ".png":
                image = image.convert("RGB")

            image.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
            image.save(target_path, "JPEG")
    except OSError:
        print("Can't create thumbnail for ", file.name)

def build_regexp_tester(regexp):
    def regexp_test_file(file):
        result = regexp.search(file.name)
        if result is None:
            return False
        else:
            return True

    return regexp_test_file


def main(argv):
    bytes_saved = 0

    if len(argv) == 0:
        print("Please provide a path.")
        quit()

    dir = Path(argv[0])

    if not dir.is_dir():
        print("Path provided is not a directory.")
        quit()

    # discard_parameters - think about making these dynanic.
    param1 = build_regexp_tester(compile(r"_400x200\..*"))
    def param2(file): return file.suffix.lower() not in [
        ".jpeg", ".png", ".jpg"]

    sort_options = {
        "discard_parameters": [param1, param2]
    }

    discard_pile: list[Path] = []
    work_queue: list[Path] = []

    sort_file = build_sort_machine(discard_pile, work_queue, sort_options)

    # Iterate through dir and sort files into discard_pile or work_queue.
    for file in dir.iterdir():
        if not file.name.startswith("."):
            sort_file(file)

    # Create a dir inside the image folder for storing thumbnails.
    target_dir = dir.joinpath(NEW_DIRECTORY)
    target_dir.mkdir(exist_ok=True)

    # Iterate over work_queue and reduce images.
    for file in work_queue:
        (current_path, target_path) = generate_file_paths(file, target_dir)
        reduce_image(file, current_path, target_path)

        # This is for personal gratification.
        bytes_saved += file.stat().st_size - Path(target_path).stat().st_size

    print("Conversion complete.")
    print("You saved " + str(round(bytes_saved/1e+6)) + " MB today.")


main(sys.argv[1:])
