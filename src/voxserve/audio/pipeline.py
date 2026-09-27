import asyncio 

from voxserve.audio.capture import MicrophoneCapture, AudioFrame

class AudioPipeline:
    def __init__(self, max_queue_size: int = 50):
        self.queue: asyncio.Queue[AudioFrame] = asyncio.Queue(maxsize=max_queue_size)

    def put_frame_nowait(self, frame: AudioFrame):
        self.queue.put_nowait(frame)
    
    async def consume(self):
        while True:
            frame = await self.queue.get()

            print(
                f"Consumed frame {frame.sequence_number}"
            )

            self.queue.task_done()