# Maze Agent

Autonomous maze-solving agent using Claude Code via subprocess.

## Requirements

- Python 3.13+
- Claude Code CLI installed and accessible as `claude.cmd`
- uv (recommended) or pip for package management

## Installation

### Using uv (recommended)

```bash
uv sync
```

### Using pip

```bash
pip install -e .
```

## Usage

Run the maze agent using the command-line interface:

```bash
maze-agent
```

Or run directly with Python:

```bash
python -m maze_agent.cli.main
```

## Development

### Project Structure

This project follows the standard src package structure:

```
maze_agent/
├── .python-version          # Python version specification
├── pyproject.toml           # Project dependencies and configuration
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── .prompt.py              # Reused prompts across projects
├── .compile.py             # Linting and cleaning commands
├── .security.py            # Security scanning commands
├── .env.example            # Environment variable template
├── logs/                   # Application logs
├── backups/                # Project backups
├── docs/
│   ├── plans/              # Development plans
│   │   └── implemented/    # Completed plans
│   └── shared_context/     # Shared documentation
└── src/
    └── maze_agent/
        ├── __init__.py
        ├── agent.py        # Core agent logic
        ├── cli/            # Command-line interface
        │   ├── __init__.py
        │   └── main.py     # CLI entry point
        └── common/         # Shared utilities
            ├── __init__.py
            ├── claude_client.py   # Claude API client
            └── action_parser.py   # Response parser
```

### Linting and Formatting

Run linting and formatting checks:

```bash
python .compile.py
```

### Security Checks

Run security scans:

```bash
python .security.py
```

## How It Works

The agent:
1. Receives a maze scenario description
2. Calls Claude Code via subprocess to make decisions
3. Parses Claude's response to extract actions
4. Executes actions in the maze environment
5. Repeats until the maze is solved or max iterations reached

## License

MIT

