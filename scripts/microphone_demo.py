import sounddevice as sd
import asyncio

from voxserve.audio.pipeline import AudioPipeline
from voxserve.audio.capture import MicrophoneCapture

SAMPLE_RATE = 16_000
FRAME_DURATION_MS = 20

SAMPLES_PER_FRAME = int(
    SAMPLE_RATE * FRAME_DURATION_MS / 1000
)

capture = MicrophoneCapture(
    sample_rate=SAMPLE_RATE,
    frame_duration_ms=FRAME_DURATION_MS,
)


def audio_callback(indata, frames, time, status):
    frame = capture.create_frame(indata)

    print(
        f"frame={frame.sequence_number}",
        f"shape={frame.samples.shape}",
        f"time={frame.timestamp:.6f}",
    )


async def main():
    capture = MicrophoneCapture(
        sample_rate=SAMPLE_RATE,
        frame_duration_ms=FRAME_DURATION_MS,
    )

    pipeline = AudioPipeline(max_queue_size=50)

    loop = asyncio.get_running_loop()

    consumer_task = asyncio.create_task(
        pipeline.consume()
    )

    def audio_callback(indata, frames, time, status):
        frame = capture.create_frame(indata)

        loop.call_soon_threadsafe(
            pipeline.put_frame_nowait,
            frame,
        )

        
    print("Streaming microphone...")
    print("Press Enter to stop.\n")
    

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=SAMPLES_PER_FRAME,
        callback=audio_callback,
    ):
        await asyncio.to_thread(input)
    
    consumer_task.cancel()


if __name__ == "__main__":
     asyncio.run(main())



