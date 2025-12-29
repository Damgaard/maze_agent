# Project Overview

This is an LLM-based autonomous agent that solves mazes using Claude AI. Built as a learning project to explore agentic AI patterns, tool use, and state management.

## Purpose

This project demonstrates:

- **Agentic AI patterns**: Autonomous decision-making loops
- **LLM tool use**: Claude's tool calling capabilities
- **State management**: Tracking game state across interactions
- **Cost tracking**: Monitoring API token usage
- **Dual execution modes**: Debug (interactive) and Production (autonomous)

## Architecture

### Project Structure

This utilizes the standard Python src structure:

```
maze_agent/
├── docs/              # Documentation
├── mazes/             # Maze definition files (ASCII format)
├── src/
│   └── maze_agent/
│       ├── cli/       # Command-line interfaces
│       │   ├── main.py           # Entry point for solve command
│       │   └── list_mazes.py     # Maze listing utility
│       ├── common/    # Business logic shared across components
│       │   ├── action_parser.py  # Parse LLM responses
│       │   ├── claude_client.py  # Claude API abstraction
│       │   ├── maze_loader.py    # Load and parse maze files
│       │   └── maze_state.py     # Game state management
│       └── agent.py   # Core agent orchestration logic
├── tests/             # Unit tests
└── pyproject.toml     # Project configuration
```

### Three-Layer Architecture

The project follows a clean layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│      CLI Layer (Interface)          │
│  • main.py - Command parsing        │
│  • list_mazes.py - Utility commands │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Agent Layer (Orchestration)       │
│  • agent.py                          │
│    - Agent loop execution            │
│    - Conversation management         │
│    - Tool execution coordination     │
│    - Token tracking                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Common Layer (Core Logic)         │
│  • maze_state.py - Game state       │
│  • maze_loader.py - Maze parsing    │
│  • claude_client.py - API calls     │
│  • action_parser.py - JSON parsing  │
└─────────────────────────────────────┘
```

**Layer Responsibilities:**

1. **CLI Layer**: User interface and command-line argument parsing
2. **Agent Layer**: Orchestrates the autonomous agent loop, manages conversation history, and coordinates tool execution
3. **Common Layer**: Reusable business logic for maze operations, state management, and LLM communication

## Data Flow

### Production Mode Flow

```
User → CLI → Agent → Claude API → Tool Executor → Maze State
                ↑____________________________________|
                     (Conversation loop)
```

### Debug Mode Flow

```
User → CLI → Agent → status.txt → Human → Claude Code CLI → response.txt → Agent → Maze State
```

**Production Mode**: Fully autonomous API-based execution with tool calling
**Debug Mode**: Step-by-step interactive mode for learning and debugging

## Key Components

### agent.py - The Orchestrator

- **run_agent_production()**: Autonomous API-based execution
- **run_agent_debug()**: Interactive step-by-step mode
- Manages conversation history and token tracking
- Implements the agent loop pattern with action limits

### maze_state.py - State Management

- Tracks current room, action count, and move history
- Manages secret door revelation state
- Provides game status descriptions to the LLM
- Validates navigation attempts

### claude_client.py - LLM Communication

- Abstracts Anthropic API interactions
- Handles tool use loop (multi-turn tool calling)
- Supports multiple Claude models (Haiku, Sonnet, Opus)
- Tracks token usage for cost monitoring

### maze_loader.py - Maze Parser

- Parses ASCII maze files into structured data
- Identifies rooms, doors, and secret passages
- Builds navigation graph from visual representation

## Technologies

- **Python 3.13**: Modern Python with latest features
- **Anthropic API**: Claude AI models (Haiku, Sonnet, Opus)
- **uv**: Fast Python package manager
- **pytest**: Testing framework
- **ruff**: Linting and code formatting

## Key Design Patterns

- **State Pattern**: MazeState encapsulates game state
- **Facade Pattern**: claude_client.py hides API complexity
- **Strategy Pattern**: Debug vs Production execution modes
- **Tool Executor Pattern**: Extensible tool handling for LLM

## Usage

```bash
# Debug mode (interactive)
uv run solve --maze 1

# Production mode (autonomous)
uv run solve --prod --maze 1

# List available mazes
uv run maze-list
```

## Further Documentation

- **[02_maze_representation.md](02_maze_representation.md)**: In-depth explanation of maze file format and structure
- **[03_cost_protection.md](03_cost_protection.md)**: Cost control strategies and token tracking implementation
- **[README.md](../README.md)**: Quick start guide and installation instructions
