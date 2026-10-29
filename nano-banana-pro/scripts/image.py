#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai",
#     "pillow",
# ]
# ///
"""
Generate images using Google's Gemini 2.5 Flash (Nano Banana Pro).

Usage:
    python -m uv run image.py --prompt "A colorful abstract pattern" --output "./hero.png"
    python -m uv run image.py --prompt "Minimalist icon" --output "./icon.png" --aspect landscape
    python -m uv run image.py --prompt "Similar style image" --output "./new.png" --reference "./existing.png"
"""

import argparse
import os
import sys
import time

from google import genai
from PIL import Image


def get_aspect_instruction(aspect: str) -> str:
    """Return aspect ratio instruction for the prompt."""
    aspects = {
        "square": "Generate a square image (1:1 aspect ratio).",
        "landscape": "Generate a landscape/wide image (16:9 aspect ratio).",
        "portrait": "Generate a portrait/tall image (9:16 aspect ratio).",
    }
    return aspects.get(aspect, aspects["square"])


def generate_image(
    prompt: str, output_path: str, aspect: str = "square", reference: str | None = None
) -> None:
    """Generate an image using Gemini 2.5 Flash and save to output_path."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    aspect_instruction = get_aspect_instruction(aspect)
    full_prompt = f"{aspect_instruction} {prompt}"

    # Build contents with optional reference image
    contents: list = []
    if reference:
        if not os.path.exists(reference):
            print(f"Error: Reference image not found: {reference}", file=sys.stderr)
            sys.exit(1)
        ref_image = Image.open(reference)
        contents.append(ref_image)
        full_prompt = f"{full_prompt} Use the provided image as a reference for style, composition, or content."
    contents.append(full_prompt)

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=contents,
    )

    # Handle retries on rate limiting
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=contents,
            )
            break
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                retry_count += 1
                if retry_count >= max_retries:
                    print(
                        f"Error: Rate limit exceeded after {max_retries} retries. "
                        "Please wait a few minutes and try again.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                wait_time = 2 ** retry_count  # Exponential backoff: 2, 4, 8 seconds
                print(
                    f"Rate limited. Retrying in {wait_time} seconds... (attempt {retry_count}/{max_retries})"
                )
                time.sleep(wait_time)
            else:
                raise

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Extract image from response
    for part in response.parts:
        if part.text is not None:
            print(f"Model response: {part.text}")
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            print(f"Image saved to: {output_path}")
            return

    print("Error: No image data in response", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Gemini 2.5 Flash (Nano Banana Pro)"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Description of the image to generate",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path (PNG format)",
    )
    parser.add_argument(
        "--aspect",
        choices=["square", "landscape", "portrait"],
        default="square",
        help="Aspect ratio (default: square)",
    )
    parser.add_argument(
        "--reference",
        help="Path to a reference image for style/composition guidance (optional)",
    )

    args = parser.parse_args()
    generate_image(args.prompt, args.output, args.aspect, args.reference)


if __name__ == "__main__":
    main()
