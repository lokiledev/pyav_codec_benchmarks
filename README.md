# PyAV codec benchmarks

A suite of tests to help me better understand how PyAV and ffmpeg works.
Also to identify what codecs are available and what is the expected performance
between gpu (ie using nvenc) and cpu encoding.

## Installation

Requires [uv](https://docs.astral.sh/uv/guides/install-python/)

```sh
uv sync
```

## Run

* Benchmark different h264 and av1 codecs encoding speed and compression
```
uv run bench_codecs.py
```

* Benchmark h264 codec with various image resolutions.
```
uv run bench_h264_encoding_speed.py
```

# Last Results

## Benchmark Constants
- **Number of frames encoded:** 1800
- **FPS:** 30
- **Total duration of clip:** 60.00 seconds

## Encoding Performance Results

| Resolution | Codec | Encoding Time/Frame (ms) | Real Time Ratio | Compressed Size (MB) | Extrapolated 1h Size (MB) |
|------------|-------|-------------------------|-----------------|---------------------|---------------------------|
| 320x240 | x264 | 1.28 | 0.04x | 3.94 | 236.7 |
| 320x240 | h264_nvenc | 1.46 | 0.04x | 14.45 | 867.0 |
| 320x240 | svtav1 | 0.24 | 0.01x | 2.66 | 159.8 |
| 320x240 | av1_nvenc | 0.37 | 0.01x | 13.90 | 834.0 |
| 640x480 | x264 | 2.55 | 0.08x | 11.01 | 660.3 |
| 640x480 | h264_nvenc | 0.74 | 0.02x | 14.47 | 868.4 |
| 640x480 | svtav1 | 0.69 | 0.02x | 6.43 | 385.9 |
| 640x480 | av1_nvenc | 0.77 | 0.02x | 14.64 | 878.2 |
| 848x480 | x264 | 3.11 | 0.09x | 13.22 | 793.0 |
| 848x480 | h264_nvenc | 0.95 | 0.03x | 14.33 | 859.7 |
| 848x480 | svtav1 | 0.91 | 0.03x | 7.67 | 460.5 |
| 848x480 | av1_nvenc | 0.95 | 0.03x | 14.67 | 880.5 |
| 1280x800 | x264 | 5.72 | 0.17x | 26.98 | 1618.9 |
| 1280x800 | h264_nvenc | 2.30 | 0.07x | 14.24 | 854.4 |
| 1280x800 | svtav1 | 2.53 | 0.08x | 13.54 | 812.5 |
| 1280x800 | av1_nvenc | 2.32 | 0.07x | 14.91 | 894.4 |
