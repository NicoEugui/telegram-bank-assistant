import subprocess


def convert_ogg_to_wav(ogg_path: str, wav_path: str) -> None:
    cmd = [
        "ffmpeg", "-y",
        "-i", ogg_path,
        "-ar", "16000",
        "-ac", "1",
        wav_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
