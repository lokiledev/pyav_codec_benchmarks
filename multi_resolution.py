import time
from datetime import timedelta
from fractions import Fraction
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Generator

import av
from PIL import Image
from tqdm import tqdm

FRAMERATE = 30
"""Default framerate for the benchmark."""


def load_frames(src_images: Path) -> Generator[Image.Image, None, None]:
    for image in src_images.iterdir():
        img = Image.open(image)
        yield img


def load_frames_task(src_images: Path, queue: Queue[Image.Image | None]):
    for frame in load_frames(src_images):
        queue.put(frame)
    queue.put(None)


def resize_frames_task(
    resolution: tuple[int, int],
    in_queue: Queue[Image.Image | None],
    out_queue: Queue[Image.Image | None],
):
    while img := in_queue.get():
        if img.size != resolution:
            img = img.resize(resolution)
        out_queue.put(img)
    out_queue.put(None)


def encode_frames(
    src_images: Path,
    resolution: tuple[int, int],
    codec_name: str,
) -> tuple[float, int]:
    """Measure the encoding performance of a sequence of video frames using given codec_name."""

    codec = av.Codec(codec_name, "w")
    codec_ctx = codec.create()
    codec_ctx.pix_fmt = "yuv420p"
    codec_ctx.width, codec_ctx.height = resolution
    codec_ctx.framerate = Fraction(FRAMERATE, 1)
    codec_ctx.time_base = Fraction(1, FRAMERATE)
    codec_ctx.max_b_frames = 0
    codec_ctx.gop_size = 15
    codec_ctx.options = {"crf": "30"}
    total_size = 0
    total_time = 0

    n_frames = len(list(src_images.glob("*.png")))
    desc = f"{resolution[0]}x{resolution[1]}-{codec_name}"
    load_queue: Queue[Image.Image | None] = Queue()
    resize_queue: Queue[Image.Image | None] = Queue()

    load_thread = Thread(target=load_frames_task, args=(src_images, load_queue))
    resize_thread = Thread(
        target=resize_frames_task, args=(resolution, load_queue, resize_queue)
    )
    load_thread.start()
    resize_thread.start()
    try:
        for _ in tqdm(
            range(n_frames),
            desc=desc,
            total=n_frames,
        ):
            img = resize_queue.get()
            if img is None:
                break
            frame = av.VideoFrame.from_image(img)
            t1 = time.perf_counter()
            packets = codec_ctx.encode(frame)
            total_time += time.perf_counter() - t1
            total_size += sum(packet.size for packet in packets)
    finally:
        if codec_ctx.is_open:
            codec_ctx.encode()
            codec_ctx.flush_buffers()

    duration = timedelta(seconds=total_time)
    return n_frames, duration, total_size


def print_stats(stats: dict):
    for codec in stats:
        print(f"{codec}:")
        for resolution in stats[codec]:
            print(
                f"  {resolution}: {stats[codec][resolution]['duration']} {stats[codec][resolution]['total_size']}"
            )


def format_stats_table(stats: dict):
    """Format stats as a nice markdown table with constants and detailed metrics."""

    first_codec = next(iter(stats))
    first_resolution = next(iter(stats[first_codec]))
    n_frames = stats[first_codec][first_resolution]["n_frames"]
    clip_duration_seconds = n_frames / FRAMERATE

    print("## Benchmark Constants")
    print(f"- **Number of frames encoded:** {n_frames}")
    print(f"- **FPS:** {FRAMERATE}")
    print(f"- **Total duration of clip:** {clip_duration_seconds:.2f} seconds")
    print()

    print("## Encoding Performance Results")
    print()
    print(
        "| Resolution | Codec | Encoding Time/Frame (ms) | Real Time Ratio | Compressed Size (MB) | Extrapolated 1h Size (MB) |"
    )
    print(
        "|------------|-------|-------------------------|-----------------|---------------------|---------------------------|"
    )

    # Sort resolutions for consistent output
    all_resolutions = set()
    for codec_data in stats.values():
        all_resolutions.update(codec_data.keys())
    sorted_resolutions = sorted(all_resolutions)

    for resolution in sorted_resolutions:
        for codec_name in stats:
            if resolution in stats[codec_name]:
                data = stats[codec_name][resolution]

                encoding_time_seconds = data["duration"].total_seconds()
                encoding_time_per_frame_ms = (encoding_time_seconds / n_frames) * 1000
                real_time_ratio = encoding_time_seconds / clip_duration_seconds
                compressed_size_mb = data["total_size"] / (1024 * 1024)
                extrapolated_1h_size_mb = compressed_size_mb * (
                    3600 / clip_duration_seconds
                )
                resolution_str = f"{resolution[0]}x{resolution[1]}"
                codec_display = codec_name.replace("lib", "")
                print(
                    f"| {resolution_str} | {codec_display} | {encoding_time_per_frame_ms:.2f} | {real_time_ratio:.2f}x | {compressed_size_mb:.2f} | {extrapolated_1h_size_mb:.1f} |"
                )

    print()


def main(images_dir: str):
    src_images = Path(images_dir)

    resolutions = [
        (320, 240),
        (640, 480),
        (848, 480),
        (1280, 800),
        (1920, 1080),
    ]

    stats = {
        "libx264": {},
        "h264_nvenc": {},
        "libsvtav1": {},
        "av1_nvenc": {},
    }
    for codec in stats:
        for resolution in resolutions:
            n_frames, duration, total_size = encode_frames(
                src_images, resolution, codec
            )
            stats[codec][resolution] = {
                "n_frames": n_frames,
                "duration": duration,
                "total_size": total_size,
            }

    format_stats_table(stats)


if __name__ == "__main__":
    import fire

    fire.Fire(main)
