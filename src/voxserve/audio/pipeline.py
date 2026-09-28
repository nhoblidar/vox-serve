import asyncio
from collections import deque

from voxserve.audio.capture import AudioFrame
from voxserve.audio.vad import (
    EnergyVAD,
    VADState,
    VADStateMachine,
)

from pathlib import Path
from voxserve.audio.writer import save_utterance_wav

class AudioPipeline:
    def __init__(
        self,
        max_queue_size: int = 50,
        pre_roll_frames: int = 15,
    ):
        self.queue: asyncio.Queue[AudioFrame] = asyncio.Queue(
            maxsize=max_queue_size
        )

        self.pre_roll = deque(
            maxlen=pre_roll_frames
        )

        self.vad = EnergyVAD(
            threshold=100
        )

        self.vad_state = VADStateMachine(
            speech_start_frames=3,
            speech_end_frames=25,
        )

        self.current_utterance: list[AudioFrame] = []

        self.utterance_count = 0

        self.output_dir = Path("recordings")
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def put_frame_nowait(
        self,
        frame: AudioFrame,
    ):
        try:
            self.queue.put_nowait(frame)

        except asyncio.QueueFull:
            print(
                f"QUEUE FULL: dropping frame "
                f"{frame.sequence_number}"
            )

    async def consume(self):
        while True:
            frame = await self.queue.get()

            try:
                # 1. Frame-level VAD
                is_speech = self.vad.is_speech(frame)

                # 2. Update state machine
                event = self.vad_state.update(is_speech)

                # 3. Handle speech start
                if event == "speech_started":
                    # Add the current frame to pre-roll
                    # before copying it.
                    self.pre_roll.append(frame)

                    self.current_utterance = list(
                        self.pre_roll
                    )

                    print(
                        f"\n>>> SPEECH STARTED "
                        f"frame={frame.sequence_number}"
                    )

                # 4. Already speaking
                elif self.vad_state.state == VADState.SPEECH:
                    self.current_utterance.append(frame)

                # 5. Speech ended
                if event == "speech_ended":
                    # Explicitly include the frame that
                    # caused the transition.
                    self.current_utterance.append(frame)

                    duration_seconds = (
                        len(self.current_utterance)
                        * 0.020
                    )

                    print(
                        f">>> SPEECH ENDED "
                        f"frame={frame.sequence_number}"
                    )

                    print(
                        f">>> UTTERANCE "
                        f"frames={len(self.current_utterance)} "
                        f"duration={duration_seconds:.2f}s"
                    )
                    
                    self.utterance_count += 1
                    output_path = self.output_dir / f"utterance_{self.utterance_count}.wav"
                    save_utterance_wav(self.current_utterance, output_path)

                    print(f">>> SAVED UTTERANCE TO {output_path}")


                    self.current_utterance = []

                    # We're back in silence.
                    # Start a fresh pre-roll history.
                    self.pre_roll.clear()

                # 6. Maintain pre-roll during silence
                elif self.vad_state.state == VADState.SILENCE:
                    self.pre_roll.append(frame)

            finally:
                self.queue.task_done()