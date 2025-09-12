import time
import typing

import av

from utils import make_image


def encode_frames(
    frames: typing.Iterable[av.VideoFrame], codec_name: str
) -> typing.Sequence[av.Packet]:
    """Measure the encoding performance of a sequence of video frames using given codec_name."""

    frame_size = frames[0].width, frames[0].height
    codec = av.Codec(codec_name, "w")
    codec_ctx = codec.create()
    print(f"{codec_name} is hwaccel: {codec_ctx.is_hwaccel}")
    try:
        codec_ctx.pix_fmt = "yuv420p"
        codec_ctx.width, codec_ctx.height = frame_size
        codec_ctx.framerate = 20

        packets = []
        packets += codec_ctx.encode(frames[0])
        t1 = time.time()
        for frame in frames[1:]:
            packets += codec_ctx.encode(frame)
        packets += codec_ctx.encode()
        t2 = time.time()
    finally:
        if codec_ctx.is_open:
            codec_ctx.flush_buffers()

    fps = (len(frames) - 1) / (t2 - t1)
    print(f"Encoded at {fps:.1f} fps ({codec_name})")
    return packets


if __name__ == "__main__":
    frames = [make_image(1920, 1080, i, 30) for i in range(30)]
    encode_frames(frames, "h264")
    encode_frames(frames, "libx264")
    encode_frames(frames, "h264_nvenc")
