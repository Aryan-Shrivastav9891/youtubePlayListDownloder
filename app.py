"""YouTube Playlist Downloader — a small Streamlit front-end for yt-dlp.

Paste a video or playlist URL, pick MP3 audio or MP4 video, and download the
result straight from the browser. Built to deploy on Streamlit Community Cloud.
"""

import os
import tempfile
import zipfile
from pathlib import Path

import streamlit as st
import yt_dlp

MEDIA_EXTS = (".mp3", ".mp4", ".m4a", ".webm", ".opus")

st.set_page_config(page_title="YouTube Playlist Downloader", page_icon="🎵")

st.title("🎵 YouTube Playlist Downloader")
st.caption("Download a YouTube video or playlist as MP3 audio or MP4 video.")

url = st.text_input(
    "YouTube video or playlist URL",
    placeholder="https://www.youtube.com/playlist?list=...",
)

col1, col2 = st.columns(2)
with col1:
    fmt = st.radio("Format", ["MP3 (audio)", "MP4 (video)"], index=0)
with col2:
    quality = st.selectbox("MP3 quality (kbps)", ["320", "256", "192", "128"], index=0)

limit = st.number_input(
    "Max items from a playlist (0 = all)", min_value=0, max_value=200, value=10, step=1,
    help="Keep this small on Streamlit Cloud — long playlists can hit the time/memory limit.",
)

start = st.button("Download", type="primary", disabled=not url.strip())


def build_opts(outdir: str, on_progress) -> dict:
    """yt-dlp options for the chosen format, writing into ``outdir``."""
    opts = {
        "outtmpl": os.path.join(outdir, "%(playlist_index)s-%(title)s.%(ext)s"),
        "ignoreerrors": True,
        "quiet": True,
        "noprogress": True,
        "noplaylist": False,
        "progress_hooks": [on_progress],
    }
    if limit:
        opts["playlistend"] = int(limit)

    if fmt.startswith("MP3"):
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": quality,
        }]
    else:
        opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        opts["merge_output_format"] = "mp4"
    return opts


if start and url.strip():
    progress = st.progress(0.0, text="Starting…")
    status = st.empty()

    def on_progress(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                frac = min(d.get("downloaded_bytes", 0) / total, 1.0)
                name = os.path.basename(d.get("filename", ""))
                progress.progress(frac, text=f"Downloading {name}")
        elif d.get("status") == "finished":
            status.info(f"Processing {os.path.basename(d.get('filename', ''))}…")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            with yt_dlp.YoutubeDL(build_opts(tmp, on_progress)) as ydl:
                ydl.download([url.strip()])
        except Exception as exc:  # noqa: BLE001 — surface any yt-dlp error to the user
            st.error(f"Download failed: {exc}")
            st.stop()

        media = sorted(p for p in Path(tmp).iterdir()
                       if p.is_file() and p.suffix.lower() in MEDIA_EXTS)
        if not media:
            st.warning(
                "No files were downloaded. The content may be private, removed, "
                "or blocked for this server's IP. Try again or a different URL."
            )
            st.stop()

        # Hold the bytes in session_state so the download button survives reruns.
        if len(media) == 1:
            f = media[0]
            st.session_state["downloads"] = [(f.name, f.read_bytes())]
        else:
            zip_path = os.path.join(tmp, "playlist.zip")
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for p in media:
                    zf.write(p, arcname=p.name)
            st.session_state["downloads"] = [("playlist.zip", Path(zip_path).read_bytes())]

    progress.progress(1.0, text="Done!")
    st.success(f"Downloaded {len(media)} file(s).")


for name, data in st.session_state.get("downloads", []):
    st.download_button(f"⬇️ Download {name}", data, file_name=name)