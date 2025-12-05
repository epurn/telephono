from PIL import Image
from pathlib import Path
import math
import json
import wave
import os
import numpy as np
from scipy.signal import ShortTimeFFT

def _load_wavs(path, color):
    wav_paths = []
    path_no_ext, ext = path.rsplit(".", 1)
    if color:
        wav_paths.append(path_no_ext + "_r" + "." + ext)
        wav_paths.append(path_no_ext + "_g" + "." + ext)
        wav_paths.append(path_no_ext + "_b" + "." + ext)
    else:
        wav_paths.append(path_no_ext + "_s" + "." + ext)
    
    wav_ars = []
    for p in wav_paths:
        with wave.open(p, "rb") as f:
            frames = f.readframes(f.getnframes())
        wav_ars.append(np.frombuffer(frames, dtype=np.int16))
    return wav_ars

def _load_metadata(path):
    meta_path = path.lstrip(".").lstrip("\\").rsplit(".")[0] + ".metadata"
    with open(meta_path, "rb") as f:
        meta = json.load(f)
    return meta

def _pad_or_trim(in_ars, shape) -> list[np.ndarray]:
    out_ar = []
    out_h, out_w = shape

    for ar in in_ars:
        ar_trim = ar[:out_h, :out_w] # Trim first
        h, w = ar_trim.shape

        # Pad Height
        if  h < out_h:
            pad_h = out_h - h

            # Pad with middle value for color, experiment with this
            ar_trim = np.pad(ar_trim, ((0, pad_h), (0, 0)), mode="constant", constant_values=128)

        # Pad Width
        if w < out_w:
            pad_w = out_w - w
            
            # Pad with middle value for color, experiment with this
            ar_trim =  np.pad(ar_trim, ((0, 0), (0, pad_w)), mode="constant", constant_values=128) 
        
        out_ar.append(ar_trim)

    return out_ar


def _convert_to_rgb(wav_ars, n_fft, hop_length, sample_rate, f_max_bin, f_min_bin, gamma):
    rgb_ars = []
    for wav_ar in wav_ars:
        in_wav_ar = wav_ar.astype(np.float32) / 32767.0
    

        stfft = ShortTimeFFT(
            win=np.hanning(n_fft),
            hop=hop_length,
            fs=sample_rate,
            mfft=n_fft)

        band_height = f_max_bin - f_min_bin + 1
        mag_ar = np.abs(stfft.stft(in_wav_ar))
        img_ar = mag_ar[f_min_bin:f_min_bin+band_height] 
        img_ar = (img_ar*255.0*gamma).clip(0, 255).astype(np.uint8)
        img_ar = np.flipud(img_ar)
        rgb_ars.append(img_ar)
    return rgb_ars


def convert_wav(path, gamma=0.6):
    args = _load_metadata(path)
    
    wav_ars = _load_wavs(path=path, color=args["color"])
    
    rgb_ars = _convert_to_rgb(wav_ars, gamma=gamma, **{k: args.get(k, None) for k in ("n_fft", "hop_length", "sample_rate", "f_max_bin", "f_min_bin")})

    if not args["color"]:
        img = Image.fromarray(rgb_ars[0], mode='L')
    else:
        # we need all input arrays to be the same length
        bal_ars = rgb_ars.copy()
        bal_ars = _pad_or_trim(bal_ars, 
            (
                min(ar.shape[0] for ar in bal_ars),
                min(ar.shape[1] for ar in bal_ars)
            )
        )
        in_ar = np.stack(bal_ars, axis=-1)
        img = Image.fromarray(in_ar, mode='RGB')
    img = img.resize((args["orig_w"], args["orig_h"]), Image.Resampling.BICUBIC)

    out_name = os.path.splitext(os.path.basename(path))[0] + "_recovered.png"
    out_name = os.path.join("out_img", out_name)
    out_path = Path(out_name)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path