# Esuyo AI Skills

Public collection of agent skills.

## Skills

### nano-banana-pro

Image generation via Google's Gemini 2.5 Flash (`gemini-2.5-flash-image`).

- Skill: `nano-banana-pro/SKILL.md`
- Script: `nano-banana-pro/scripts/image.py`

#### Prerequisites

Set `GEMINI_API_KEY`:

```bash
export GEMINI_API_KEY="your-key"
```

#### Usage

```bash
uv run nano-banana-pro/scripts/image.py \
  --prompt "A minimalist geometric hero image" \
  --output "./hero.png"

# With options
uv run nano-banana-pro/scripts/image.py \
  --prompt "Abstract pattern" \
  --output "./wide.png" \
  --aspect landscape \
  --reference "./existing.png"
```

Options:
- `--prompt` (required): image description
- `--output` (required): output PNG path
- `--aspect`: `square` | `landscape` | `portrait` (default: `square`)
- `--reference`: reference image path for style/composition guidance

See `nano-banana-pro/SKILL.md` for prompt guidance and frontend integration.

## License

See [LICENSE](./LICENSE).
