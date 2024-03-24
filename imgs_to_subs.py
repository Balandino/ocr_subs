import os
import subprocess
from string import punctuation

import PySimpleGUI as psg


def load_dictionary() -> set[str]:
    """
    Loads the dictionary of English words

    Returns:
        Dictionary of English words
    """
    with open("words_alpha.txt") as word_file:
        valid_words = set(word_file.read().split())

    return valid_words


def reload_dictionary():
    """Reloads the global ENGLISH_WORDS to the latest dictionary"""
    global ENGLISH_WORDS
    ENGLISH_WORDS = load_dictionary()


def getTimestamp(img: str) -> str:
    """
    Extracts an srt formatted timestamp for subtitles from the image name

    Args:
        img: Name of image extracted using VideoSubFinder

    Returns: String timestamp

    """
    split_name = img.split("_")
    start_time = f"{split_name[0]}:{split_name[1]}:{split_name[2]},{split_name[3]}"
    end_time = f"{split_name[5]}:{split_name[6]}:{split_name[7]},{split_name[8]}"
    return f"{start_time} --> {end_time}"


def check_words(text: str) -> list[str]:
    """
    Checks the words in the text against a dictionary of error_words

    Args:
        text: String of text to be split apart and checked

    Returns:
        List of error words, or empty list if none found

    """
    words = text.split()
    error_words = []
    for word in words:
        word = word.lower().strip(punctuation)

        if word not in ENGLISH_WORDS and word != "":
            error_words.append(word)

    print(error_words)
    return error_words


def dictGUI(words: list[str]) -> list[str]:
    """
    Generates a GUI for the user to confirm new lines to be added to the dictionary

    Args:
        words: List of words to check

    Returns:
        List of words to add to dictionary
    """
    heading = psg.Text(
        "Words to add to dictionary",
        expand_x=True,
        justification="center",
    )

    text = "\n".join(words)

    textarea = psg.Multiline(
        text,
        enable_events=True,
        key="-INPUT-",
        expand_x=True,
        expand_y=True,
        font=("Verdana", 20),
        size=(60, 10),
        justification="left",
    )

    ok_button = psg.Button("Ok", key="-OK-", font=("Verdana", 20))
    exit_button = psg.Button("Exit", font=("Verdana", 20))
    none_button = psg.Button("None", key="-NONE-", font=("Verdana", 20))
    back_button = psg.Button("Back", key="-BACK-", font=("Verdana", 20))

    layout = [[heading], [textarea], [ok_button, none_button, back_button, exit_button]]
    window = psg.Window("Lines to add to dictionary", layout, finalize=True)
    window.bind("<Alt_L><o>", "ALT-o")
    window.bind("<Alt_L><n>", "ALT-n")
    window.bind("<Alt_L><x>", "ALT-x")
    window.bind("<Alt_L><b>", "ALT-b")

    ok_button.Widget.configure(underline=0, takefocus=0)  # pyright: ignore
    none_button.Widget.configure(underline=0, takefocus=0)  # pyright: ignore
    exit_button.Widget.configure(underline=1, takefocus=0)  # pyright: ignore
    back_button.Widget.configure(underline=0, takefocus=0)  # pyright: ignore

    window.TKroot.focus_force()
    window.Element("-INPUT-").SetFocus()

    while True:
        event, values = window.read()  # pyright: ignore
        if event in (psg.WIN_CLOSED, "Exit", "ALT-x"):
            quit()

        if event in ("-OK-", "ALT-o"):
            error_words = values["-INPUT-"].split("\n")
            break

        if event in ("-NONE-", "ALT-n"):
            error_words = []
            break

        if event in ("-BACK-", "ALT-b"):
            error_words = ["-BACK-"]
            break

    window.close()

    if len(error_words) == 1 and error_words[0] == "":
        return []

    return error_words


def inputGUI(text: str, img_pathway: str, title: str) -> str:
    """
    Displays a GUI with an image and the text tesseract thinks it shows.  User can confirm or alter
    the text.

    Args:
        text: Text to display
        img_pathway: Pathway to image to show
        title: Title of window

    Returns:
        Text to be used in subtitles
    """
    heading = psg.Text(
        title,
        font=("Verdana", 20),
        expand_x=True,
        justification="center",
    )
    textarea = psg.Multiline(
        text,
        enable_events=True,
        key="-INPUT-",
        font=("Verdana", 30),
        expand_x=True,
        expand_y=True,
        size=(0, 5),
        justification="left",
    )

    image = psg.Image(img_pathway, expand_x=True, expand_y=True)
    ok_button = psg.Button("Ok", key="-OK-", font=("Verdana", 20))
    none_button = psg.Button("None", key="-NONE-", font=("Verdana", 20))
    exit_button = psg.Button("Exit", font=("Verdana", 20))

    layout = [[image], [heading], [textarea], [ok_button, none_button, exit_button]]
    window = psg.Window("Confirm Subtitles", layout, finalize=True)
    window.bind("<Alt_L><o>", "ALT-o")
    window.bind("<Alt_L><n>", "ALT-n")
    window.bind("<Alt_L><x>", "ALT-x")

    ok_button.Widget.configure(underline=0, takefocus=0)  # pyright: ignore
    none_button.Widget.configure(underline=0, takefocus=0)  # pyright: ignore
    exit_button.Widget.configure(underline=1, takefocus=0)  # pyright: ignore

    window.TKroot.focus_force()
    window.Element("-INPUT-").SetFocus()
    while True:
        event, values = window.read()  # pyright: ignore
        if event in (psg.WIN_CLOSED, "Exit", "ALT-x"):
            quit()

        if event in ("-OK-", "ALT-o"):
            subtitle_text = values["-INPUT-"]
            break

        if event in ("-NONE-", "ALT-n"):
            subtitle_text = ""
            break

    window.close()
    return subtitle_text


def getPNGS() -> list[str]:
    """
    Returns list of png images for processing

    Returns:
        List of image pathways
    """
    imgs = []

    for file in os.listdir(IMAGES_DIR):
        if file.endswith(".png"):
            imgs.append(file)

    return imgs


def addWordsToDict(error_words: list[str]) -> bool:
    """
    Adds new words to dictionary and then reloads it

    Args:
        error_words: List of error words
    """
    words_to_add = dictGUI(error_words)

    if words_to_add == ["-BACK-"]:
        return False

    if len(words_to_add) < 1:
        return True

    with open("words_alpha.txt", "a") as dictionary:
        for word in words_to_add:
            dictionary.write(f"{word}\n")

    reload_dictionary()
    return True


def runTesseract(img_pathway: str) -> str:
    """
    Runs tesseract from command line over img

    Args:
        img_pathway: Pathway to image to process

    Returns:
        Stripped output from stdout
    """
    # tesseract --tessdata-dir 'C:\Users\Michael\tessdata' .\0_01_46_073__0_01_49_609_3000003910720008707200480.jpeg - -l eng
    command = [
        "tesseract",
        "--tessdata-dir",
        "C:\\Users\\Michael\\tessdata",
        img_pathway,
        "-",
        "-l",
        "eng",
        "--psm",
        "6",
        "quiet",
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8").strip()


def writeSubs(subtitles: str):
    """
    Writes string to srt file

    Args:
        subtitles: Text to write
    """
    with open("Output.srt", "w") as subs:
        subs.write(subtitles)


def preprocessText(text: str) -> str:
    """
    Does some basic pre-processing to remove common translation errors beforehand

    Args:
        text: Text from tesseract

    Returns:
        Text for further processing
    """

    text = text.replace("|", "I")  # | always seems to be I, so replace
    text = text.replace("’", "'")  # Apostrophe often interpreted as odd quotes
    text = text.replace("‘", "'")  # NOT THE SAME CHARACTER AS ABOVE, DON'T DELETE
    text = text.replace(" iam ", " I am")
    text = text.replace(" ima ", " i'm a")
    return text


def runner(MAX_COUNT):
    imgs = getPNGS()

    total_output = ""
    count = 1
    for img in imgs:
        timestamp = getTimestamp(img)
        img_pathway = f"{IMAGES_DIR}\\{img}"
        cmd_output = runTesseract(img_pathway)
        cmd_output = preprocessText(cmd_output)
        error_words = check_words(cmd_output)

        # Whole text is error words, take gamble and skip
        if len(error_words) == len(cmd_output.split()):
            continue

        if len(error_words) > 0:
            while True:
                cmd_output = inputGUI(
                    cmd_output, img_pathway, f"No. {count}/{len(imgs)}"
                )
                print("=====================")
                print(error_words)
                print("=====================")
                complete = addWordsToDict(error_words)
                if complete:
                    break

        if len(cmd_output.strip()) == 0:
            continue

        output = f"{count}\n{timestamp}\n{cmd_output}\n\n"
        print(output)

        total_output += output
        count = count + 1
        if MAX_COUNT > 0 and count == MAX_COUNT:
            break

    writeSubs(total_output)


IMAGES_DIR = "C:\\Video Sub Finder\\TXTImages"
ENGLISH_WORDS = load_dictionary()

# Set below 1 to run to end
runner(0)

