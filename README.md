# Telephono

This is just a quick python project I put together in order to test out a photography concept I had. Feel free to try it out and suggest features. 😊

This application allows you to convert images into playable audio files (spectrograms), these files can then be recorded and converted back to images.

## Pre-Requisites

### [Python 3.12](https://www.python.org/downloads/release/python-31212/)

Just install the appropriate version for your system, make sure you add it to your PATH. You'll also need the pip package manager

```bash
python -m pip install
```

### [Git](https://git-scm.com/downloads) and the source code

Same with python, get a version for your system. Make sure it's on the PATH. Clone the git repo wherever your heart desires:

```bash
git clone https://github.com/epurn/telephono.git
cd ./telephono
```

### All libraries in requirements.txt

From the root of the repo

```bash
pip install -r requirements.txt
```

### Optional steps

#### Create a virtual env

Not required but always recommended when working with python. Steps to create and activate it on...

* Windows

```powershell
python -m venv .venv
.venv/Scripts/Activate.ps1
```

* Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

#### Download [Audacity](https://www.audacityteam.org/download/)

Useful tool for viewing spectrograms (wav files) and for recording audio. Just get the version for your platform without the "Muse Hub" installer.

#### Create the input/output folders

Just keeps things organized

```bash
mkdir in_img out_wav in_wav out_img
```

## Installation

Nothing to install!

## Usage

The application runs in two modes, specified via the -m parameter.

### Image Mode (I)

Image Mode allows you to convert any image supported by [pillow](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html) to a single wav file or set of wav files (one per color channel).

There are a number of arguments available to adjust the conversion. You can run the application with the -h or --help flag at any time to get an overview of the args. Here is a complete list of the image mode args:

| Argument      | Description                                               | Type                     | Required | Default |
| ------------- | --------------------------------------------------------- | ------------------------ | -------- | ------- |
| -p or --path  | The path of the input image                               | valid path to image file | Yes      | N/A     |
| -m or --mode  | The mode of the application                               | I for image mode         | Yes      | N/A     |
| -c or --color | Do you want the result to be color? Don't include for B&W | Flag                     | No       | False   |
| --min-hz      | The minimum frequency of the spectrogram                  | Integer                  | No       | 400     |
| --max-hz      | The maximum frequency of the spectrogram                  | Integer                  | No       | 6000    |

#### Tips

* Larger images look better, but have a longer duration. Still, if you can stand the noise, it's worth it for more interesting results. The duration of the file is directly influenced by the size of the image. The goal is to lose as little information as possible.
* min-hz and max-hz should be set based on your speaker frequency and mic frequency. The defaults are a relatively safe range.
* You'll notice a .metadata file, this should be saved as it will need to be re-used with the recorded audio.

### WAV Mode (W)

WAV mode converts any recorded spectrogram back into an image. The input WAV or WAVs must be mono-channel, signed 16-bit PCM, and have a sample rate of 44100 Hz.

There are just a few args for this mode. The most important thing is that your WAVs and your .metadata file are in the same directory.

| Argument     | Description                           | Type                     | Required | Default |
| ------------ | ------------------------------------- | ------------------------ | -------- | ------- |
| -p or --path | The path of the input image           | valid path to image file | Yes      | N/A     |
| -m or --mode | The mode of the application           | W for WAV mode           | Yes      | N/A     |
| --gamma      | The brightness of the resulting image | Float                    | No       | 0.3     |

#### Tips

* Ensure you name your re-recorded WAVs with the same name as the originals. I.e. photo_r.wav photo_g.wav, photo_b.wav for color mode; photo_s.wav for B&W mode.
* Make sure your .metadata file is in the same place as your re-recorded WAV files. Your dir should look like this:

```
in_wav/
├── photo_r.wav
├── photo_g.wav
├── photo_b.wav
├── photo.metadata
```

* Experiment with gamma if your image is too dark or too light.

## Examples:

### Convert from base image in color mode

```bash
python ./telephono.py -m I -p in_img/DSCF1636.jpg -c --min-hz 400 --max-hz 7000
```

this will create the files:

```
out_wav/
├── DSCF1361_r.wav
├── DSCF1361_g.wav
├── DSCF1361_b.wav
├── DSCF1361.metadata
```

### Convert re-recorded files to image

```bash
# Note that you have to use ORIGINAL_FILENAME.wav, even though that file does not exist.
python ./telephono.py -m W -p in_wav/DSCF1636.wav --gamma 0.2
```

this will create the file

```
out_img/
├── DSCF1361_recovered.png
```
