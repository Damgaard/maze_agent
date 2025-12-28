# Maze Agent

A LLM based Maze solver. Built as a learning experience in agentic development.

## Installation

```bash
uv sync
```

## Configuration

For production mode (API-based), you need to configure your Anthropic API key:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your-api-key-here
   CLAUDE_MODEL=sonnet
   ```

   Get your API key from: https://console.anthropic.com/

3. (Optional) Choose your Claude model:
   - `haiku` - Fast and cost-effective (claude-3-5-haiku-20241022)
   - `sonnet` - Balanced performance (claude-sonnet-4-20250514) **[Default]**
   - `opus` - Maximum capability (claude-opus-4-5-20251101)
   - `default` - Same as sonnet

   Models use hardcoded versions to avoid unexpected changes.

## Usage

### Debug Mode (Interactive)

Run the agent in debug mode using Claude Code CLI:

```bash
uv run solve --maze 1
```

This mode:
- Uses `status.txt` and `response.txt` files
- Allows step-by-step interaction
- Calls Claude Code CLI (`claude.cmd`)

### Production Mode (Autonomous)

Run the agent in production mode using the Anthropic API:

```bash
uv run solve --prod --maze 1
```

This mode:
- Fully autonomous operation
- Direct API calls to Claude
- No file I/O required
- Requires `ANTHROPIC_API_KEY` in `.env`

### List Available Mazes

```bash
uv run maze-list
```

### Using Different Models

To use a different Claude model, set the `CLAUDE_MODEL` environment variable in your `.env` file:

```bash
# Use Haiku for faster, more cost-effective solving
CLAUDE_MODEL=haiku

# Use Opus for maximum capability
CLAUDE_MODEL=opus

# Use Sonnet (default)
CLAUDE_MODEL=sonnet
```

Or set it temporarily for a single run:
```bash
CLAUDE_MODEL=opus uv run solve --prod --maze 3
```

##