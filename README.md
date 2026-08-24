# Oblique Thinking MCP

An MCP server exposing one tool, `ObliqueStrategies`, which returns a
random Oblique Strategy.

## Install

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/janbam/oblique-thinking-mcp.git && cd oblique-thinking-mcp && uv sync --frozen
```

The project currently pins `mcp[cli]==2.0.0`.

## Run

```bash
uv run --frozen server.py
```

The optional mode argument changes the output:

- No argument: thinking prompt and strategy card
- `1`: strategy card only
- `2`: thinking prompt only

For example:

```bash
uv run --frozen server.py 1
```

## Claude Desktop

Add this to `claude_desktop_config.json` and replace the directory with the
absolute path to your clone:

```json
{
  "mcpServers": {
    "oblique-thinking": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/oblique-thinking-mcp",
        "--frozen",
        "server.py",
        "1"
      ]
    }
  }
}
```

The final `"1"` selects card-only mode. Remove it for the combined output or
replace it with `"2"` for thinking-prompt-only mode.

## Test

```bash
uv run --frozen python -m unittest discover -s tests -v
```
