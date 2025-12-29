# Maze Solver

LLM based Agents to solve Mazes. A Agentic flow learning project.

## Goal

Evaluate flows if an LLM can successfully solve a maze. The Maze contains both regular doors and secret doors, that the LLM must first look for. So to solve the maze, an LLM must build an internal model of the maze with doors, secret doors and whether it has looked for secret doors in that room. There is, deliberately, little context given upon entering a room.

### Learnings

The following are some raw learnings from this project.

- Claude Code is _not_ a optimized way of Claude. It is a purpose built wrapper around Claude for coding purposes. It is built with strong text editing capabilities and understandings of the tools available on local dev. It is optimized for coding, with automatic context awareness of the built-in code and with a prompt to look into codebase to seek answer to questions. It cannot be used for more generic purposes, like solving mazes. The work around used in this project is ok for learning projects, it will not work for actual production projects.
- Tools are the "hands" of the LLM that it uses to resolve questions during thinking, before it returns an answer. These are simple text, that need to be translated by the recipient to actual calls ( there may be tools that go elsewhere, like websearches ).
- By default, resolving a tool usage requires sending the full previous message list. This mean that this can quickly built up the length of the input tokens.
- Cost control is important. Each API call == money spent. We must track tokens used to understand cost of a conversation.
- We must keep a full record of a conversation. This allows replaying it later, as well as using it for debugging for unexpected behaviour.

### Bugs

This is meant as learning project for how agentic AI works. The advantages of it. How best to structure a project for agents and their quirks.

I don't care if this project actually builds and solves mazes correctly. Any bugs related to this is not that important.

## Project

The following outlines the actual project and main concepts.

### Usage

First copy `env.example` to `.env` and update credentials with your API key. Then run

```bash
uv sync
uv run solve --prod
```

This solves a simple maze using Claude's API. You can run `uv run solve --help` to get full list of options available for this command.

Also useful is `uv run maze-list`, which outputs a list of available mazes and a small description of them.

### Mazes

Each possible maze can be found in the /mazes directory. It should be fairly straighforward, as the mazes are fairly simple. There is extensive documentation of the mazes in the [docs/02_maze_representation.md](docs/02_maze_representation.md) file, note that this is intended for LLM usage. So it quite.... verbose.

### Debug mode

To increase dev speed, a debug mode has also been created. In this case, the project runs against a local Claude Code instance instead of the API. This is also step based and require human assistance to progress. This allows for slower, more granular understanding of the project.

To use debug mode run `uv run solve` in terminal tab 1, then in tab 2 run `claude`. Now within the claude CLI give it the following prompt "Read @status.txt and follow instructions". It will read the initial prompt and give a json response of it's intended action as well as the thinking behind. Now go back to the first terminal tab window and press Enter. This will make the solver load in the response from Claude Code and continue the next step.

Go back into Claude, give it the same prompt, and then go back to Terminal tab 1. Continue this flow until the task is completed.
