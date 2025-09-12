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