## Features

* Splits lossless Audio CD images into individual FLAC tracks using CUE sheets.
* Supported image formats: APE, FLAC, WAVPACK, WAV.
* Tracks are tagged and named regarding to CUE.

## Requirements

* Python >= 2.7
* cuetools package (e.g. `apt-get install cuetools`)
* shntool package (e.g. `apt-get install shntool`)
* flac package (e.g. `apt-get install flac`)
* Optional: wavpack package (e.g. `apt-get install wavpack`) if you need WavPack support
* Optional: monkeys-audio package if you need APE format support. See [Debian monkeys-audio packages](http://pkgs.org/download/monkeys-audio) for instance.

## Usage

Basic program usage from console looks like this:

```
python imgsplit.py path/to/dir
```

Or if you make the script executable with `chmod +x imgsplit.py`

```
./imgsplit.py path/to/dir
```

where path/to/dir is a path to the directory containing both image file and CUE sheet.

The convention is that both CUE sheet and image should be named similarly, e.g. "CDImage.cue" and "CDImage.ape", "Wonderful Disk Vol.1.cue" and "Wonderful Disk Vol.1.flac". There can be more than one cue/image pair in the same folder, so file names should match each other. For each matching cue/image pair the script creates a subfolder with a similar name and puts splitted tracks into it.

There's just one option currently, -r or --remove:

```
./imgsplit.py -r "~/music/Wonderful Disk Vol.2"
```

This option tells the script to remove the original CUE/image after splitting is finished successfully.
