"""Sources package - Video input sources and sample generation."""

from sources.video_source import VideoSource
from sources.sample_generator import generate_sample_data

__all__ = [
    "VideoSource",
    "generate_sample_data",
]

