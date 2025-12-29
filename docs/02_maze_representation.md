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
3. **Trailing newline**: Exactly 1 empty line at the end

### Example Maze File:

```
=== MAZE 01: Simple North Exit ===
One door to the north leads directly to exit.

#####
#...#
#.E.#
#...#
#####
  D
#####
#...#
#.S.#
#...#
#####

```

---

## Symbol Definitions

| Symbol      | Meaning     | Description                                                                                |
| ----------- | ----------- | ------------------------------------------------------------------------------------------ |
| `#`         | Wall        | Solid barrier, cannot pass through                                                         |
| `.`         | Room Floor  | Walkable area inside a room                                                                |
| `S`         | Start       | Player's starting position (center of room)                                                |
| `E`         | Exit        | Goal position (center of room), maze is solved when reached                                |
| `D`         | Door        | Visible door connection between rooms (single character in middle)                         |
| `X`         | Secret Door | Hidden door, only visible after using search_secrets() action (single character in middle) |
| ` ` (space) | Empty       | Area outside the maze structure                                                            |

---

## Room Structure

### 3x3 Interior

Every room has a **3x3 interior space**:

```
#####
#...#  <- Top row of room interior
#.S.#  <- Middle row (markers go here)
#...#  <- Bottom row of room interior
#####
```

- Rooms are always enclosed by `#` (walls)
- Interior is filled with `.` (floor)
- Markers (`S` or `E`) are placed in the **center position** of the 3x3 grid

---

## Understanding Doors

### Visible Doors

Visible doors are represented by the character **`D`** placed as a single character in the middle position between two rooms.

**Example - Vertical Door (North/South):**

```
#####
#...#
#.E.#  <- Room above
#...#
#####
  D    <- Door connection (middle position)
#####
#...#
#.S.#  <- Room below
#...#
#####
```

**Example - Horizontal Door (East/West):**

```
##### #####
#...# #...#
#.S.#D#.E.#  <- Door connection in middle
#...# #...#
##### #####
```

### Secret Doors

Secret doors are marked with `X` and are **not visible** until the player uses the `search_secrets()` action.

**Example - Secret Door to the North:**

```
#####
#...#
#.E.#
#...#
#####
  X    <- Secret Door (hidden until discovered)
#####
#...#
#.S.#
#...#
#####
```

### No Connection

When there is no door, the space between rooms shows `#` (walls continue):

**Example - No Door (Blocked):**

```
#####
#...#
#.E.#
#...#
#####
  #    <- No door, just wall continuation
#####
#...#
#.S.#
#...#
#####
```

---

## Reading Room Layouts

### Single Room (No Doors)

```
#####
#...#
#.S.#
#...#
#####
```

- A room enclosed by walls (`#`)
- 3x3 interior with `.` floor
- Start position (`S`) in the center
- All sides are walls (no connections)

### Two Rooms with Door

```
#####
#...#
#.E.#
#...#
#####
  D    <- Visible door
#####
#...#
#.S.#
#...#
#####
```

- Two vertically stacked rooms
- `D` between them = visible door
- Player can move from S room to E room by going north

### 2x2 Grid Example

```
##### #####
#...# #...#
#...#D#.E.#
#...# #...#
##### #####
  D     D
##### #####
#...# #...#
#.S.#D#...#
#...# #...#
##### #####
```

- Four rooms in a 2x2 grid
- Horizontal doors shown as `D` between side-by-side rooms
- Vertical doors shown as `D` in the row between stacked rooms
- Each door indicator is a single character in the middle position

---

## Creating New Mazes

### Step-by-Step Guide

1. **Choose a number**: Pick the next available number (e.g., if you have 01-08, create 09)

2. **Design the layout**: Plan rooms and connections on paper first

3. **Create the file**: Name it `XX_description.txt`

4. **Write the header**:

   ```
   === MAZE XX: Description ===
   Brief explanation of the maze layout.
   ```

5. **Draw the maze**:

   - Each room is 5 characters wide (`#####`)
   - Each room has 3x3 interior (`.` for floor)
   - Place `S` or `E` in the center of their rooms
   - Use `D` for visible door connections (single character, middle position)
   - Use `X` for secret door connections (single character, middle position)
   - Use `#` for wall continuations (no door)
   - Separate side-by-side rooms with a space column
   - Separate stacked rooms with a space row

6. **End the file**: Ensure exactly 1 empty line at the end

### Template

```
=== MAZE XX: [Name] ===
[Description of the maze]

#####
#...#
#.E.#
#...#
#####
  D
#####
#...#
#.S.#
#...#
#####

```

---

## Maze Design Rules

1. **Every maze must have exactly one Start (S) position**
2. **Every maze must have exactly one Exit (E) position**
3. **All rooms must have 3x3 interior space using `.` for floor**
4. **All rooms must be enclosed by walls (`#`)**
5. **Doors use explicit characters: `D` for visible, `X` for secret**
6. **Door characters are single characters placed in the middle position between rooms**
7. **Rooms are connected vertically or horizontally, not diagonally**
8. **A room can have 0-4 doors (North, South, East, West)**
9. **Secret doors (`X`) should only be discoverable via the search_secrets() action**
10. **Files must end with exactly 1 empty line**
11. **No legend section in maze files**

---

## Common Patterns

### Dead End Room

```
#####
#...#
#...#
#...#
#####
  D    <- Only one door (the entrance)
```

A room with only one connection - the door you came through.

### Corridor Room

```
  D    <- Door north
#####
#...#
#...#
#...#
#####
  D    <- Door south
```

A room with doors on opposite sides, creating a corridor.

### Linear Path (3 Rooms)

```
#####
#...#
#.E.#
#...#
#####
  D
#####
#...#
#...#
#...#
#####
  D
#####
#...#
#.S.#
#...#
#####
```

Three rooms vertically connected, start at bottom, exit at top.

---

## Interpreting Maze State in Code

When implementing maze logic, you need to:

1. **Parse the file** to extract room positions and connections
2. **Track current room** based on player position
3. **Check available doors** from current room:
   - Look for `D` characters adjacent to the current room
   - Secret doors (`X`) are only available after search_secrets() is called
4. **Validate movement**: Only allow movement through visible doors (`D` or discovered `X`)
5. **Check win condition**: Player reached the room with `E`

### Parsing Notes

- Each room occupies 5 columns and 5 rows
- Room interior is always the middle 3x3 area
- Door connections are single characters:
  - For vertical connections: Check the middle position of the row between rooms
  - For horizontal connections: Check the middle position of the column between rooms
- Markers (`S`, `E`) are always in the center cell of the 3x3 interior

---

## Examples from Existing Mazes

### Maze 01: Simple Linear Path

```
01_simple_north.txt
- Start room has one door north (D)
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
- Start has door south (D) and secret door north (X)
- South leads to dead end
- Secret north leads to exit
- Solution: search_secrets(), then navigate("north")
- Wrong solution: navigate("south") leads to dead end
```

### Maze 06: 2x2 Grid

```
06_grid_2x2_connected.txt
- 2x2 grid with all rooms connected via visible doors
- Multiple valid paths from start to exit
- Demonstrates horizontal and vertical door placement
```

---

## Summary

**To read a maze:**

1. Look at the visual grid
2. Find `S` (start) and `E` (exit) in room centers
3. Identify visible doors as `D` characters
4. Identify secret doors as `X` characters
5. Rooms are 5x5 blocks with 3x3 interior

**To create a maze:**

1. Use naming convention `XX_name.txt`
2. Draw header with title and description
3. Each room: 5x5 with 3x3 interior using `.` for floor
4. Place `S` and `E` in center of their rooms
5. Use `D` for visible doors, `X` for secret doors
6. End file with exactly 1 empty line
7. Test that there's a solvable path from S to E
