# Maze Representation Format

**Intended Audience:** LLMs (Large Language Models)

This document describes the maze file format used in this project. Understanding this format allows you to read maze files and create new mazes.

---

## File Naming Convention

Maze files are located in the `mazes/` directory and follow this naming pattern:

```
XX_descriptive_name.txt
```

- **XX**: Two-digit zero-padded maze number (01, 02, 03, etc.)
- **descriptive_name**: Brief description of the maze
- **Extension**: Always `.txt`

**Examples:**
- `01_simple_north.txt`
- `02_corridor_north.txt`
- `15_complex_labyrinth.txt`

**To load maze 1:** Find the file starting with `01_`
**To load maze 15:** Find the file starting with `15_`

---

## Visual Format Structure

Each maze file contains:

1. **Header**: Title and description
2. **Visual Grid**: ASCII art representation of the maze
3. **Legend**: Symbol definitions

### Example Maze File:

```
=== MAZE 01: Simple North Exit ===
One door to the north leads directly to exit.

#####
# E #
#   #
#####
  #    <- Door North
#####
#   #
# S #
#####

Legend:
S = Start position
E = Exit position
# = Wall
(space) = Open floor
```

---

## Symbol Definitions

| Symbol | Meaning | Description |
|--------|---------|-------------|
| `#` | Wall | Solid barrier, cannot pass through |
| `S` | Start | Player's starting position |
| `E` | Exit | Goal position, maze is solved when reached |
| `X` | Secret Door | Hidden door, only visible after using search_secrets() action |
| ` ` (space) | Open Floor | Walkable area inside a room |
| Door Gap | Opening in walls | Absence of `#` character between rooms indicates a door |

---

## Understanding Doors

### Visible Doors

Doors are represented as **gaps in the wall**. Look for missing `#` characters between room boundaries.

**Example - Door to the North:**
```
#####
#   #  <- Room above
#####
  #    <- Gap = Door North (visible)
#####
#   #  <- Current room
#####
```

The gap in the wall (where you'd expect `###` but see ` # `) is a visible door.

### Secret Doors

Secret doors are marked with `X` and are **not visible** until the player uses the `search_secrets()` action.

**Example - Secret Door to the North:**
```
#####
#   #  <- Room above
#####
  X    <- Secret Door North (hidden until discovered)
#####
#   #  <- Current room
#####
```

---

## Reading Room Layouts

### Single Room
```
#####
# S #
#   #
#####
```
- A room enclosed by walls (`#`)
- Start position (`S`) inside
- All sides are walls (no doors)

### Room with North Door
```
#####
# E #
#   #
#####
  #    <- Door opening (visible)
#####
#   #
# S #
#####
```
- Two vertically stacked rooms
- Gap in the wall between them = door
- Player can move from S room to E room by going north

### Room with Multiple Doors
```
#####
# E #
#   #
#####
  #    <- North door
#####
#   # #   <- East door (gap on right)
#####
  #    <- South door
#####
```

---

## Creating New Mazes

### Step-by-Step Guide

1. **Choose a number**: Pick the next available number (e.g., if you have 01-05, create 06)

2. **Design the layout**: Plan rooms and connections on paper first

3. **Create the file**: Name it `XX_description.txt`

4. **Write the header**:
   ```
   === MAZE XX: Description ===
   Brief explanation of the maze layout.
   ```

5. **Draw the maze**:
   - Use `#` for all walls
   - Place `S` at the start position
   - Place `E` at the exit position
   - Create door gaps by omitting `#` characters
   - Use `X` for secret doors

6. **Add the legend**: Always include the symbol legend at the bottom

### Template

```
=== MAZE XX: [Name] ===
[Description of the maze]

#####
# E #
#   #
#####
  #    <- [Direction] door (visible/secret)
#####
#   #
# S #
#####

Legend:
S = Start position
E = Exit position
# = Wall
X = Secret door (not visible without searching)
(space) = Open floor
```

---

## Maze Design Rules

1. **Every maze must have exactly one Start (S) position**
2. **Every maze must have exactly one Exit (E) position**
3. **All rooms must be enclosed by walls (`#`)**
4. **Doors are represented by gaps in walls, not by special characters** (exception: `X` for secret doors)
5. **Rooms are connected vertically or horizontally, not diagonally**
6. **A room can have 0-4 doors (North, South, East, West)**
7. **Secret doors (`X`) should only be discoverable via the search_secrets() action**

---

## Common Patterns

### Dead End Room
```
#####
#   #
#   #  <- Only one door (the entrance)
#####
  #    <- Door south
```
A room with only one exit - the door you came through.

### Corridor Room
```
  #    <- Door north
#####
#   #
#####
  #    <- Door south
```
A room with doors on opposite sides, creating a corridor.

### Junction Room
```
  #    <- Door north
#####
#   # #  <- Doors east and west
#####
  #    <- Door south
```
A room with multiple doors, creating choices.

---

## Interpreting Maze State in Code

When implementing maze logic, you need to:

1. **Parse the file** to extract room positions and connections
2. **Track current room** based on player position
3. **Check available doors** from current room:
   - Look for gaps in walls around the current room
   - Secret doors (`X`) are only available after search_secrets() is called
4. **Validate movement**: Only allow movement through visible doors
5. **Check win condition**: Player reached the room with `E`

---

## Examples from Existing Mazes

### Maze 01: Simple Linear Path
```
01_simple_north.txt
- Start room has one door north
- North leads directly to exit
- Solution: navigate("north")
```

### Maze 03: Secret Required
```
03_secret_north.txt
- Start room has NO visible doors
- Has secret door north (marked with X)
- Solution: search_secrets(), then navigate("north")
```

### Maze 05: Wrong Path + Secret
```
05_secret_vs_deadend.txt
- Start has door south (visible) and secret door north
- South leads to dead end
- Secret north leads to exit
- Solution: search_secrets(), then navigate("north")
- Wrong solution: navigate("south") leads to dead end
```

---

## Notes for Implementation

- When parsing mazes, preserve spatial relationships between rooms
- Empty lines in the visual representation are formatting only
- Comments (with `<-`) are for human readability, ignore in parsing
- The legend is documentation, not parsed data
- Room boundaries are defined by continuous `#` characters
- A "door" programmatically means the player can issue a navigate(direction) command

---

## Summary

**To read a maze:**
1. Look at the visual grid
2. Find `S` (start) and `E` (exit)
3. Identify doors as gaps in `#` walls
4. Note `X` for secret doors

**To create a maze:**
1. Use naming convention `XX_name.txt`
2. Draw with `#`, `S`, `E`, and `X` symbols
3. Gaps in walls = visible doors
4. Include header and legend
5. Test that there's a solvable path from S to E
