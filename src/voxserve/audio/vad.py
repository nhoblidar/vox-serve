import numpy as np
from enum import Enum

from voxserve.audio.capture import AudioFrame


class EnergyVAD:
    def __init__(self, threshold: float):
        self.threshold = threshold

    def compute_rms(self, frame: AudioFrame) -> float:
        samples = frame.samples.astype(np.float32)

        rms = np.sqrt(
            np.mean(samples ** 2)
        )

        return float(rms)

    def is_speech(self, frame: AudioFrame) -> bool:
        rms = self.compute_rms(frame)

        return rms >= self.threshold


class VADState(Enum):
    SILENCE = "silence"
    SPEECH = "speech"


class VADStateMachine:
    def __init__(
        self,
        speech_start_frames: int = 3,
        speech_end_frames: int = 25,
    ):
        self.state = VADState.SILENCE

        self.speech_start_frames = speech_start_frames
        self.speech_end_frames = speech_end_frames

        self.speech_count = 0
        self.silence_count = 0

    def update(self, is_speech: bool):
        if self.state == VADState.SILENCE:

            if is_speech:
                self.speech_count += 1
            else:
                self.speech_count = 0

            if self.speech_count >= self.speech_start_frames:
                self.state = VADState.SPEECH
                self.speech_count = 0

                return "speech_started"

        elif self.state == VADState.SPEECH:

            if not is_speech:
                self.silence_count += 1
            else:
                self.silence_count = 0

            if self.silence_count >= self.speech_end_frames:
                self.state = VADState.SILENCE
                self.silence_count = 0

                return "speech_ended"

        return None