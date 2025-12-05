from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter, BooleanOptionalAction
from img_to_wav_STFT import convert_image
from wav_to_img_STFT import convert_wav


def _parse_args() -> Namespace:
    parser = ArgumentParser(
        description = ("Encode an image to spectrogram, then convert it back to an image after being played."),
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-p",
        "--path",
        required=True,
        help="Input path of file."
    )

    parser.add_argument(
        "-m",
        "--mode",
        required=True,
        help="--mode I for img to wav, --mode W for wav to img"
    )

    parser.add_argument(
        "--min-hz",
        type=float,
        default=400,
        help="MODE I - Lower band for frequency - useful for making image more resiliant"
    )
    
    parser.add_argument(
        "--max-hz",
        type=float,
        default=6000,
        help="MODE I - Higher band for frequency - useful for making image more resiliant"
    )

    parser.add_argument(
        "--gamma",
        type=float,
        default=0.3,
        help="MODE W - Adjusts brightness of resultant image"
    )

    parser.add_argument(
        "--color",
        "-c", 
        action=BooleanOptionalAction, 
        default=False
    )

    return parser.parse_args()


def main():
    args = _parse_args()
    if args.mode == "I":
        convert_image(args.path, min=args.min_hz, max=args.max_hz, color=args.color)
    elif args.mode == "W":
        convert_wav(args.path, gamma=args.gamma)


if __name__ == '__main__':
    main()
