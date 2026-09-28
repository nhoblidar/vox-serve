from pathlib import Path
import wave

import numpy as np

from voxserve.audio.capture import AudioFrame


def save_utterance_wav(
    frames: list[AudioFrame],
    output_path: str | Path, 
):

    if not frames:
        return 

    samples = np.concatenate(
        [frame.samples for frame in frames],
        axis=0,
    )

    output_path = Path(output_path)

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(frames[0].sample_rate)
        wav_file.writeframes(samples.astype(np.int16).tobytes())

        