# Media Pipeline

## Before Processing Any Media Link

Do not process Douyin or Xiaohongshu links until `scripts/check_environment.py --vault "<vault>"` has been run.

If it reports missing AnyContent, missing SiliconFlow API key, missing AnyContent backend, or missing ffmpeg, stop and report the missing requirements to the user first.

For Xiaohongshu routes, also require the Python package `requests`.

## Platform Decision

For normal operation, prefer the unified Capture processor:

```powershell
python scripts/process_capture_links.py --vault "<vault>" --capture-file "<capture-file>" --assume-ready
```

Use the lower-level scripts only when debugging one route.

Use this routing:

```text
Douyin video        -> AnyContent -> raw -> Source -> Knowledge
Douyin image post   -> AnyContent OCR -> raw -> Source
Xiaohongshu video   -> xhs_to_source.py -> audio transcription -> raw -> Source
Xiaohongshu image   -> xhs_to_source.py -> image OCR -> raw -> Source
Explicit save image -> save_images_from_raw.py -> _System/Attachments -> Source links
```

## Douyin

Use:

```powershell
python scripts/anycontent_to_source.py --vault "<vault>" --capture-file "<capture-file>" --index 0
```

AnyContent may create raw Markdown with transcript or image OCR. The script can generate a draft Source, but the agent must still polish it according to `source_structuring.md`.

If PowerShell output fails because of emoji or Chinese paths, inspect the generated files directly. The import may have succeeded even if console printing failed.

For Douyin image posts, AnyContent raw may include `Image content (OCR)` and `Original image URLs`. If the user wrote `保存图片`, `留图`, `下载图片`, or `下载原图` near the link, run:

```powershell
python scripts/save_images_from_raw.py --vault "<vault>" --raw-file "<raw-file>"
```

Then add the saved attachment links to the Source note.

## Xiaohongshu

Use:

```powershell
python scripts/xhs_to_source.py --vault "<vault>" --url "http://xhslink.com/o/xxxx" --write
```

For videos, the adapter resolves the share link, extracts the video stream, temporarily downloads media under `_System`, extracts audio with ffmpeg, transcribes, writes raw, then writes Source draft.

For image posts, the adapter resolves image URLs and calls a vision OCR model through the API key stored in AnyContent settings.

The adapter's default speech-to-text model is `FunAudioLLM/SenseVoiceSmall`. Its image OCR uses Qwen vision-capable models through SiliconFlow. Make sure the user's account has balance/access before assuming OCR or ASR can work.

Temporary video/audio files should be deleted after processing. Raw transcript/OCR should remain in `_System/AnyContent/raw` for traceability.

For Xiaohongshu image posts, the default is OCR only, not saving images. If the user explicitly asks to save images, run `save_images_from_raw.py` on the raw OCR file after `xhs_to_source.py` finishes.

## Known Limits

Xiaohongshu page structure can change. If parsing fails, inspect `window.__INITIAL_STATE__` extraction first.

Vision OCR may require a paid or credited API key. If OCR fails due to insufficient balance, mark the Source `needs_ocr` and keep page metadata plus raw image URLs.
