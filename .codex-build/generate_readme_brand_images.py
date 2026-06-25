#!/usr/bin/env python3
"""Generate README brand images with Gemini image generation."""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = Path(os.environ.get("KEYS_ENV", str(Path.home() / ".env")))
REFERENCE_IMAGE = Path(os.environ.get("REFERENCE_IMAGE", str(ROOT / "assets" / "style-reference.webp")))
ASSETS = ROOT / "assets"
TIMEOUT_SECONDS = 120
MODEL_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash-image:generateContent?key={key}"
)


@dataclass(frozen=True)
class Job:
    png_name: str
    webp_name: str
    prompt: str


@dataclass
class Result:
    job: Job
    ok: bool = False
    error: str | None = None
    paths: list[Path] = field(default_factory=list)


JOBS = [
    Job(
        "cover.png",
        "cover.webp",
        (
            "Wide banner image, dark charcoal background (#0d1117). On the left, "
            "a friendly orange Ferris crab (the Rust mascot) in the SAME clean "
            "flat-vector style as the attached reference, holding the black Rust "
            "cog-and-R logo. On the right, a softly glowing knowledge graph: many "
            "small nodes connected by thin lines, in Rust orange and warm sand "
            "(#DEA584). Modern, minimal, high contrast, faint terminal scanline "
            "texture. No text, no words, no letters."
        ),
    ),
    Job(
        "ferris-brain.png",
        "ferris-brain.webp",
        (
            "A friendly orange Ferris crab (same flat-vector style as the "
            "attached reference) sitting below a glowing network of interconnected "
            "nodes shaped like a brain, symbolizing a knowledge brain. Clean white "
            "background, crisp vector, Rust orange and sand accents. No text."
        ),
    ),
    Job(
        "knowledge-graph.png",
        "knowledge-graph.webp",
        (
            "A dense, beautiful knowledge-graph illustration: hundreds of small "
            "glowing dots connected by thin lines, grouped into a few clusters, "
            "in Rust orange, warm sand, and a hint of teal, on a near-black "
            "background. Looks like an Obsidian graph view, alive and "
            "interconnected. Flat, modern, no text."
        ),
    ),
    Job(
        "ferris-badge.png",
        "ferris-badge.webp",
        (
            "A clean circular badge / sticker of the friendly orange Ferris crab "
            "in the exact flat-vector style of the attached reference, centered, "
            "on a transparent or white background, with a thin Rust-orange ring. "
            "Crisp, simple, logo-like. No text."
        ),
    ),
]


def load_gemini_key(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        if name.strip() == "GEMINI_API_KEY":
            key = value.strip().strip('"').strip("'")
            if key:
                return key
    raise RuntimeError(f"GEMINI_API_KEY not found in {path}")


def find_image_part(response: dict) -> bytes:
    candidates = response.get("candidates") or []
    for candidate in candidates:
        content = candidate.get("content") or {}
        for part in content.get("parts") or []:
            inline_data = part.get("inlineData") or part.get("inline_data")
            if inline_data and inline_data.get("data"):
                return base64.b64decode(inline_data["data"])
    raise RuntimeError("Gemini response did not contain an inline image part")


def generate_png(api_key: str, reference_b64: str, job: Job) -> Path:
    body = {
        "contents": [
            {
                "parts": [
                    {"text": job.prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/webp",
                            "data": reference_b64,
                        }
                    },
                ]
            }
        ]
    }
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        MODEL_URL.format(key=api_key),
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            response_body = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"request failed: {exc}") from exc

    decoded = json.loads(response_body.decode("utf-8"))
    png_bytes = find_image_part(decoded)
    png_path = ASSETS / job.png_name
    png_path.write_bytes(png_bytes)
    return png_path


def convert_to_webp(png_path: Path, webp_path: Path) -> Path | None:
    try:
        from PIL import Image  # type: ignore

        with Image.open(png_path) as image:
            image.save(webp_path, "WEBP", quality=90)
        return webp_path
    except ImportError:
        pass

    cwebp = shutil.which("cwebp")
    if cwebp is None:
        return None

    subprocess.run(
        [cwebp, "-quiet", "-q", "90", str(png_path), "-o", str(webp_path)],
        check=True,
    )
    return webp_path


def byte_size(path: Path) -> int:
    return path.stat().st_size


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    api_key = load_gemini_key(ENV_PATH)
    reference_b64 = base64.b64encode(REFERENCE_IMAGE.read_bytes()).decode("ascii")

    results: list[Result] = []
    for index, job in enumerate(JOBS, start=1):
        print(f"[{index}/{len(JOBS)}] Generating {job.png_name}...", flush=True)
        result = Result(job=job)
        try:
            png_path = generate_png(api_key, reference_b64, job)
            result.paths.append(png_path)
            print(f"  saved PNG: {png_path}", flush=True)

            webp_path = convert_to_webp(png_path, ASSETS / job.webp_name)
            if webp_path is None:
                print("  WEBP conversion skipped: Pillow and cwebp unavailable", flush=True)
            else:
                result.paths.append(webp_path)
                print(f"  saved WEBP: {webp_path}", flush=True)
            result.ok = True
        except Exception as exc:  # Continue with remaining assets.
            result.error = str(exc)
            print(f"  ERROR: {result.error}", flush=True)
        results.append(result)

    print("\nSummary:", flush=True)
    for result in results:
        status = "OK" if result.ok else "FAIL"
        print(f"- {result.job.png_name}: {status}", flush=True)
        if result.error:
            print(f"  error: {result.error}", flush=True)
        for path in result.paths:
            print(f"  {path} ({byte_size(path)} bytes)", flush=True)

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
