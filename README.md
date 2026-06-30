# 🎵 YouTube Playlist Downloader

A tiny [Streamlit](https://streamlit.io) web app that downloads a YouTube video
or playlist as **MP3 audio** or **MP4 video**, powered by
[yt-dlp](https://github.com/yt-dlp/yt-dlp) and `ffmpeg`.

## Features

- Paste any video or playlist URL
- Choose MP3 (audio) or MP4 (video), and MP3 bitrate
- Cap how many items to pull from a playlist
- Live download progress, then a one-click browser download (zipped for playlists)

## Run locally

```bash
pip install -r requirements.txt   # streamlit + yt-dlp
# ffmpeg is required for MP3 conversion:
#   macOS:  brew install ffmpeg
#   Ubuntu: sudo apt install ffmpeg
streamlit run app.py
```

Then open http://localhost:8501.

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Pick this repo, branch `main`, and set the main file to `app.py`.
4. Deploy. `requirements.txt` installs the Python deps and `packages.txt`
   installs `ffmpeg` automatically.

## Known limitations

- **Datacenter IPs:** YouTube sometimes blocks requests from cloud servers, so
  downloads that work locally can fail on Streamlit Cloud. This is a yt-dlp /
  YouTube limitation, not a bug in this app.
- **Resource limits:** Streamlit Community Cloud has time and memory caps. Keep
  playlists small; large/long videos may time out.

## Legal

Only download content you own or have the right to download. You are responsible
for complying with YouTube's Terms of Service and applicable copyright law.
