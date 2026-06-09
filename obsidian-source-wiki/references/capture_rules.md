# Capture Rules

## Default Capture Behavior

Keep capture lightweight. The user can paste raw share text, links, or brief comments without YAML or strict formatting.

Use daily folders:

```text
00_Capture/External/YYYY-MM-DD/
00_Capture/Personal/YYYY-MM-DD/
```

## Personal vs External

Personal notes should preserve original wording and atmosphere. They are memory objects as much as knowledge material.

External content is usually for knowledge processing. It can be cleaned, transcribed, OCR'd, structured into Sources, and distilled into Knowledge.

## Image Saving Rule

Default: do not download or preserve images. Extract text/OCR and keep source links.

Save images only when the text near the link contains one of:

- `保存图片`
- `留图`
- `下载图片`
- `下载原图`
- equivalent explicit instruction

If saving images, put them under:

```text
_System/Attachments/<Platform>/YYYY-MM-DD/<source-title>/
```

Then embed or link them from the Source note.
