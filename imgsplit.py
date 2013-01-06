#!/usr/bin/env python
import argparse
import subprocess
import os
import re
from glob import glob


def check_requirements():
    "Checks if required programs are installed"

    try:
        subprocess.check_output(["cuebreakpoints", "--help"])
    except OSError:
        print "Required 'cuetools' package not found in your system."
        return False

    try:
        subprocess.check_output(["shnsplit", "-v"], stderr=os.open(os.devnull, os.O_WRONLY))
    except OSError:
        print "Required 'shntool' package not found in your system."
        return False

    try:
        subprocess.check_output(["metaflac", "--help"])
    except OSError:
        print "Required 'flac' package not found in your system."
        return False

    return True


def check_ape():
    "Checks if Monkeys Audio Codec is present"

    try:
        subprocess.check_output(["mac"], stderr=os.open(os.devnull, os.O_WRONLY))
    except subprocess.CalledProcessError:
        return True
    except OSError:
        print "Required 'monkeys-audio' package not found in your system."
        return False

    return True


def check_wv():
    "Checks if WavPack decoder is present"

    try:
        subprocess.check_output(["wvunpack", "--help"], stderr=os.open(os.devnull, os.O_WRONLY))
    except subprocess.CalledProcessError:
        return True
    except OSError:
        print "Required 'wavpack' package not found in your system."
        return False

    return True


def run_shell(cmd):
    "Runs a complex shell command"

    ret = subprocess.call(["/bin/bash", "-c", cmd])
    if ret is not 0:
        print "Command failed: %s" % cmd
        return False
    return True


def filter(name):
    "Removes invalid characters from file name"

    return re.sub(r'[":`~\?\*|\\/,{}<>]', ' ', name)


def get_valid_name(flac):
    "Gets a human friendly name for a FLAC file from its meta tags"

    number = subprocess.check_output(["metaflac", "--show-tag=TRACKNUMBER", flac])
    number = (number.partition('=')[2]).strip("\r\n\t ")

    artist = subprocess.check_output(["metaflac", "--show-tag=ARTIST", flac])
    artist = (artist.partition('=')[2]).strip("\r\n\t ")
    artist = filter(artist)

    title = subprocess.check_output(["metaflac", "--show-tag=TITLE", flac])
    title = (title.partition('=')[2]).strip("\r\n\t ")
    title = filter(title)

    return "%s - %s - %s.flac" % (number, artist, title)


def split_image(image, cue):
    "Splits an image by CUE into flac files"

    # Create a subfolder and put files there
    base = os.path.splitext(image)[0]
    parent_dir = os.getcwd()

    if not os.path.exists(base):
        os.mkdir(base)
    os.chdir(base)

    # Break image into tracks
    if not run_shell("cuebreakpoints '../%s' | shnsplit -o flac '../%s'" % (cue, image)):
        return False

    # Add meta tags to flac tracks
    if not run_shell("cuetag '../%s' *.flac" % cue):
        return False

    # Rename flac tracks to more sensible names
    flacs = glob('*.flac')
    for flac in flacs:
        valid_name = get_valid_name(flac)
        os.rename(flac, valid_name)
        print "Renamed %s => %s" % (flac, valid_name)

    # Restore context and return
    os.chdir(parent_dir)
    return True


def process_dir(path, remove_source=False):
    "Splits images in a directory using CUEs"

    # Go to target
    os.chdir(path)

    # WavPack files need unpacking first
    wvpacks = glob('*.wv')
    if len(wvpacks) > 0:
        if not check_wv():
            return False
        for wv in wvpacks:
            ret = subprocess.call(["wvunpack", "-cc", "-d", '"%s"' % wv])
            if ret is not 0:
                print "wvunpack failed on %s" % wv
                return 1

    # Get the CUEs and images
    cues = glob('*.cue')
    images = [os.path.basename(f) for f in os.listdir(path) if (os.path.splitext(f)[1]).lower() in ['.ape', '.flac', '.wav']]

    res = True

    if len(cues) > 0 and len(images) > 0:
        # Match CUE names against image names
        for cue in cues:
            base = os.path.splitext(cue)[0]
            for image in images:
                nameparts = os.path.splitext(image)
                if nameparts[0] == base:
                    if nameparts[1].lower() == '.ape' and not check_ape():
                        return False
                    if split_image(image, cue):
                        print "Success: splitted %s with %s" % (image, cue)
                        if remove_source:
                            os.remove(image)
                            os.remove(cue)
                    else:
                        print "Error: failed to split %s with %s" % (image, cue)
                        res = False
                    continue
    else:
        print "No CUEs or images found"

    return res


def main():
    p = argparse.ArgumentParser(description="Splits APE/FLAC/WAV/WV images into\
        single .flac files by CUE sheets. Image names anc CUE names should match.")
    p.add_argument('path', metavar='path', default='.', nargs='?',
        help="Directory to search for images and CUEs")
    p.add_argument('-r', '--remove', action='store_true',
        help="Remove original image and CUE")
    arguments = p.parse_args()

    if not check_requirements():
        return 1

    if not os.path.exists(arguments.path):
        print "Path does not exist: %s" % arguments.path

    current_dir = os.getcwd()
    ret = process_dir(arguments.path, arguments.remove)
    os.chdir(current_dir)
    return ret


if __name__ == '__main__':
    main()
