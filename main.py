"""
Main entry point for the podcast-mcp application.
A simple MCP server example.
"""

import re
import sys
from typing import TypedDict

from youtube_transcript_api import YouTubeTranscriptApi
from mcp.server.fastmcp import FastMCP

_api = YouTubeTranscriptApi()

# Initialize the MCP server
mcp = FastMCP(
    name="YouTube Transcript Server",
    description="Fetches plain-text transcripts for public YouTube videos"
)

_VIDEO_ID = r"(?P<id>[A-Za-z0-9_-]{11})"
_PATTERNS = [
    re.compile(rf"[?&]v={_VIDEO_ID}"),
    re.compile(rf"youtu\.be/{_VIDEO_ID}"),
    re.compile(rf"youtube(?:-nocookie)?\.com/(?:embed|v|shorts|live)/{_VIDEO_ID}"),
    re.compile(rf"^{_VIDEO_ID}$"),
]


def extract_video_id(url: str) -> str | None:
    """Return the 11-character YouTube video ID (or None if invalid)."""
    for pattern in _PATTERNS:
        match = pattern.search(url)
        if match:
            return match.group("id")
    return None


class TranscriptRequest(TypedDict):
    url: str


@mcp.tool()
def get_transcript(url: str):
    """Return the transcript of a YouTube video.

    Parameters
    ----------
    data.url : str
        Any valid YouTube watch / share / short-link URL.

    Returns
    -------
    video_id : str
        The 11-character ID of the video.
    transcript : str
        The plain-text transcript with time-codes removed.

    Raises
    ------
    ValueError
        If the URL is missing or invalid.
    youtube_transcript_api.YouTubeTranscriptApiError
        If the video has no available transcript.
    """
    if not url:
        raise ValueError("URL is required")
    
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")

    fetched = _api.fetch(video_id)
    transcript_text = " ".join(snippet.text for snippet in fetched).strip()

    return {
        "video_id": video_id,
        "transcript": transcript_text,
    }


if __name__ == "__main__":
    print("🔧 Starting YouTube Transcript MCP server...", file=sys.stderr)
    mcp.run(transport="stdio")
