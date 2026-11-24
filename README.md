# Album Art Studio

Offline Windows app to add or replace embedded cover artwork in MP3 files.

## Build the EXE with GitHub Actions
1. Upload this folder's contents to a GitHub repository.
2. Ensure `main.py` and `.github/workflows/build-exe.yml` are present.
3. Open the repository's **Actions** tab.
4. Run **Build Album Art Studio Windows EXE**.
5. Download the `Album-Art-Studio-Windows-EXE` artifact from the completed run and extract it.

This ZIP contains source code and the build workflow, not a precompiled EXE.

## Features
- Batch-select MP3 files.
- Choose and preview one JPG/PNG cover image.
- Save updated MP3 copies to a separate output folder.
- Original files are not overwritten; audio is not re-encoded.

## Local run
`python -m pip install mutagen pillow`
`python main.py`

Note: MP3 album artwork is a still image. Some keypad phones have limits on supported image formats, ID3 versions, or image dimensions, so test one file first.
