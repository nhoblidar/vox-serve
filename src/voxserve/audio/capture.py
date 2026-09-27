from dataclasses import dataclass
import numpy as np
import time

@dataclass
class AudioFrame:
    sample_rate: int
    samples: np.ndarray
    sequence_number: int
    timestamp: float


class MicrophoneCapture:
    def __init__(self, sample_rate: int, frame_duration_ms: int):
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.sequence_number = 0
        

    def create_frame(self, samples: np.ndarray) -> AudioFrame:
        frame = AudioFrame(
            sample_rate=self.sample_rate,
            samples=samples.copy(),
            sequence_number=self.sequence_number,
            timestamp=time.monotonic()
        )
        
        self.sequence_number += 1
        return frame

