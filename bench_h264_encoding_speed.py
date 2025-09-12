import time

import av
from av.codec.hwaccel import HWAccel
from av.video.stream import VideoStream

from utils import make_image


def test_pyav_encoding_benchmark() -> None:
    """Benchmark PyAV encoding performance with different configurations.

    Tests different codec, hardware acceleration, and resolution combinations
    and prints results in a markdown table format.
    """
    from typing import TypedDict

    class ConfigDict(TypedDict):
        codec: str
        hwaccel: bool

    class ResultDict(TypedDict):
        resolution: str
        config: str
        avg_ms: float
        min_ms: float
        max_ms: float
        hwaccel: str

    # Standard resolutions from 480p to 1080p
    resolutions = [
        (640, 480),  # 480p
        (1280, 720),  # 720p
        (1920, 1080),  # 1080p
    ]

    # Test configurations
    configs: list[ConfigDict] = [
        {"codec": "h264", "hwaccel": False},
        {"codec": "h264", "hwaccel": True},
        {"codec": "libx264", "hwaccel": False},
        {"codec": "libx264", "hwaccel": True},
    ]

    results: list[ResultDict] = []
    num_frames = 10  # Number of frames to encode for timing

    print("\n" + "=" * 80)
    print("PyAV Encoding Benchmark")
    print("=" * 80)

    for width, height in resolutions:
        print(f"\nTesting resolution: {width}x{height}")

        # Create test frame
        av_frame = make_image(width, height, 0, 30)

        for config in configs:
            try:
                # Create container and stream
                container = av.open("/dev/null", "w", format="h264")

                if config["hwaccel"]:
                    # Try to use hardware acceleration
                    try:
                        hwaccel = HWAccel(
                            device_type="cuda", allow_software_fallback=False
                        )
                        stream = container.add_stream(config["codec"], rate=30)
                        # Try to set hardware acceleration (may not be supported in all environments)
                        try:
                            stream.codec_context.hwaccel = hwaccel
                        except (AttributeError, TypeError):
                            # Hardware acceleration not supported, continue with software
                            pass
                    except Exception:
                        # Hardware acceleration not available, skip this config
                        container.close()
                        continue
                else:
                    stream = container.add_stream(config["codec"], rate=30)

                assert isinstance(stream, VideoStream)
                stream.width = width
                stream.height = height
                stream.max_b_frames = 0

                # Set codec options for better performance
                try:
                    codec_ctx = stream.codec_context
                    codec_ctx.options = {"g": "30", "bf": "0", "preset": "fast"}
                except Exception:
                    pass

                # Warm up - encode a few frames
                for _ in range(3):
                    try:
                        stream.encode(av_frame)
                    except Exception:
                        pass

                # Benchmark encoding
                times: list[float] = []
                for i in range(num_frames):
                    # Create a slightly different frame for each iteration
                    frame = make_image(width, height, i, 30)

                    start_time = time.perf_counter()
                    try:
                        stream.encode(frame)
                        end_time = time.perf_counter()
                        times.append(end_time - start_time)
                    except Exception as e:
                        print(f"  Error encoding with {config['codec']}: {e}")
                        times = []
                        break

                container.close()

                if times:
                    avg_time_ms = sum(times) / len(times) * 1000
                    min_time_ms = min(times) * 1000
                    max_time_ms = max(times) * 1000

                    results.append(
                        {
                            "resolution": f"{width}x{height}",
                            "config": config["codec"],
                            "avg_ms": avg_time_ms,
                            "min_ms": min_time_ms,
                            "max_ms": max_time_ms,
                            "hwaccel": "on" if config["hwaccel"] else "off",
                        }
                    )

                    print(
                        f"  {config['codec']}: {avg_time_ms:.2f}ms avg ({1000 / avg_time_ms:.1f} fps)"
                    )

            except Exception as e:
                print(f"  {config['codec']}: Failed - {e}")
                continue

    # Print results table
    print("\n" + "=" * 100)
    print("BENCHMARK RESULTS")
    print("=" * 100)
    print()
    print(
        "| Resolution | Configuration | HW Accel | Avg Time (ms) | Min Time (ms) | Max Time (ms) |"
    )
    print(
        "|------------|---------------|----------|---------------|---------------|---------------|"
    )

    for result in results:
        print(
            f"| {result['resolution']:>10} | {result['config']:>13} | {result['hwaccel']:>8} | {result['avg_ms']:>12.2f} | {result['min_ms']:>12.2f} | {result['max_ms']:>12.2f} |"
        )

    print()
    print("=" * 100)

    # Assert that we got some results
    assert len(results) > 0, "No successful encoding configurations found"


def main():
    test_pyav_encoding_benchmark()


if __name__ == "__main__":
    main()
