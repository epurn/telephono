from PIL import Image
import math
import json
import wave
import os
import numpy as np
from scipy.signal import ShortTimeFFT


def _load_image(path, color):
    if color:
        return Image.open(path).convert('RGB')
    return Image.open(path).convert('L')


def _calculate_args(img, min_hz, max_hz, color):
    orig_w, orig_h = img.size

    sample_rate = 44100
    n_fft = orig_h * 2
    stft_h = n_fft // 2 + 1

    f_min_bin = int(round(min_hz * n_fft / sample_rate))
    f_min_bin = max(0, min(f_min_bin, stft_h - 1))
    f_max_bin = int(round(max_hz * n_fft / sample_rate))
    f_max_bin = max(0, min(f_max_bin, stft_h - 1))
    
    hop_length = int(math.floor(0.25*n_fft))
    dur = (hop_length * orig_w)/sample_rate
    n_samples = int(math.floor(sample_rate * dur))
    stft_w = int(math.ceil(n_samples/hop_length))
    return {
        "orig_h": orig_h,
        "orig_w": orig_w,
        "min_hz": min_hz,
        "max_hz": max_hz,
        "f_min_bin": f_min_bin,
        "f_max_bin": f_max_bin,
        "sample_rate": sample_rate,
        "n_fft": n_fft,
        "hop_length": hop_length,
        "dur": dur,
        "n_samples": n_samples,
        "stft_h": stft_h,
        "stft_w": stft_w,
        "color": color
    }
    

def _write_metadata(path, args):
    with open(path, "w", encoding='utf-8') as f:
        json.dump(args, f)


def convert_image(path, color=False, min=400, max=6000):
    img = _load_image(path, color)
    args = _calculate_args(img, min, max, color)

    band_height = args["f_max_bin"] - args["f_min_bin"] + 1
    img = img.resize((args["stft_w"], band_height), Image.Resampling.BICUBIC)

    img_ar = np.asarray(img, dtype=float)
    img_chnls = {}
    if color:
        img_chnls['r'] = img_ar[:,:,0]
        img_chnls['g'] = img_ar[:,:,1]
        img_chnls['b'] = img_ar[:,:,2]
    else:
        img_chnls['s'] = img_ar


    for k, v in img_chnls.items():
        inv_ar = np.flipud(v)

        c_inv_arr = np.zeros((args["stft_h"], args["stft_w"]), dtype=float)
        c_inv_arr[args["f_min_bin"]:args["f_min_bin"]+img.size[1]] = inv_ar

        meta_path = os.path.join("out_wav", os.path.splitext(os.path.basename(path))[0] + ".metadata")
        _write_metadata(meta_path, args)
        
        stfft = ShortTimeFFT(
            win=np.hanning(args["n_fft"]),
            hop=args["hop_length"],
            fs=args["sample_rate"],
            mfft=args["n_fft"])
        
        wav_ar = stfft.istft(c_inv_arr)
        wav_ar = np.asarray(wav_ar, dtype=float)
        wav_ar /= np.max(np.abs(wav_ar) + 1e-9)   # avoid division by zero
        audio = (wav_ar * 32767.0).astype(np.int16)

        wav_path = os.path.join("out_wav", os.path.splitext(os.path.basename(path))[0] + "_" + k + ".wav")
        with wave.open(wav_path, "w") as f:
            f.setparams((1, 2, args["sample_rate"], args["n_samples"], "NONE", "Uncompressed"))
            f.writeframes(audio.tobytes())
        

