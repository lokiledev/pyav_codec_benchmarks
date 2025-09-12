import time
import typing

import av

from utils import make_image


def encode_frames(
    frames: typing.Iterable[av.VideoFrame], codec_name: str
) -> tuple[typing.Sequence[av.Packet], float, int]:
    """Measure the encoding performance of a sequence of video frames using given codec_name."""

    frame_size = frames[0].width, frames[0].height
    codec = av.Codec(codec_name, "w")
    codec_ctx = codec.create()
    try:
        codec_ctx.pix_fmt = "yuv420p"
        codec_ctx.width, codec_ctx.height = frame_size
        codec_ctx.framerate = 30

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
    total_size = sum(packet.size for packet in packets)
    return packets, fps, total_size


if __name__ == "__main__":
    frames = [make_image(1920, 1080, i, 30) for i in range(30)]

    # List of codecs to test
    codecs = [
        "h264",
        "libx264",
        "h264_nvenc",
        "av1",
        "av1_nvenc",
        "libaom-av1",
        "libsvtav1",
    ]

    # Collect results
    results = []
    for codec in codecs:
        _, fps, total_size = encode_frames(frames, codec)
        size_kb = total_size / 1024
        results.append((codec, fps, size_kb))

    # Print markdown table
    print("\n## Video Codec Performance Results")
    print()
    print("| Codec | FPS | Size (KB) |")
    print("|-------|-----|-----------|")
    for codec, fps, size_kb in results:
        print(f"| {codec} | {fps:.1f} | {size_kb:.1f} |")
