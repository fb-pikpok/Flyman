# Player Class Guide

This note walks through the `Player` class in `game/main.py` and explains what each part does in plain language. Think of it as a tour guide for someone who has written a little code before but has never seen this project.

## 1. Big Picture

The `Player` object keeps track of everything the little circle character needs in order to move: where it is, how fast it is moving, what state it is in (grounded, airborne, gliding), and how it should respond to keyboard input and platforms. Every frame, the game loop:

1. Reads the keyboard and calls `handle_input`.
2. Checks for a spacebar tap and calls `spacebar_event`.
3. Calls `move_and_collide` to apply forces, update the position, and resolve collisions.
4. Draws the player using the values stored on the object.

## 2. Important Data Stored on the Player

- `self.rect` - a Pygame rectangle that describes where the player sits on the screen for drawing and collision checks. The code also mirrors its position with `self.pos_x` and `self.pos_y`, which are floating-point numbers for smoother physics.
- Velocity numbers `self.vel_x` and `self.vel_y` say how fast the player moves horizontally and vertically.
- `self.input_horizontal` caches the current left/right input (`-1`, `0`, or `1`). This lets the glide code keep steering even if it tweaks velocity directly.
- A bundle of constants such as `GRAVITY`, `MOVE_SPEED`, and the `GLIDE_*` values tune how strong the different forces feel.
- `self.facing`, a 2D vector that points where the player is currently travelling. The little nose triangle on the sprite uses it.
- `self.movement_state`, a string with one of three values: `"grounded"`, `"airborne"`, or `"gliding"`.

## 3. Method-by-Method Tour

### `__init__(self, x, y, radius)`
Sets up the player. It creates the rectangle, remembers the start position, and fills in all the default physics numbers. If you imagine the player as a paper airplane, this method folds the airplane and sets it onto the starting tile.

### `handle_input(self, keys)`
Reads the keyboard each frame. If the `A` key is pressed, the stored horizontal input becomes `-1`; if `D` is pressed it becomes `+1`; pressing neither keeps it at `0`. When the player is not gliding, the method directly sets `vel_x` to a constant walking speed in the chosen direction.

*Why it matters:* While gliding, we cannot simply overwrite the velocity (otherwise the glide math would be wiped out). Storing the intent in `self.input_horizontal` gives the glide code a clean signal to work with.

### `try_jump(self)`
If the player is standing on the ground, this sets the vertical velocity to a negative number (negative means "going up" in our coordinate system) and switches the movement state to `"airborne"`. It does nothing if called while mid-air - a safety check so you cannot start an infinite jump chain.

### `start_glide(self)`
This only runs when the player is already airborne. The method decides a launch direction (prefer the current velocity, then current input, then the last facing direction). It then converts some falling speed into sideways motion, clamps vertical speed so the player neither rockets up nor drops like a stone, and switches to the `"gliding"` state.

*Kid-friendly analogy:* imagine leaping off a ledge with a hang glider. As soon as you pull back on the bar, you turn your downward fall into forward swoop. This function performs that conversion and sets up the glide behaviour.

### `spacebar_event(self)`
Called once when the spacebar is tapped. It decides whether that tap should be a jump (if grounded) or a glide trigger (if airborne). Centralising the logic here keeps the event handling code in `main` short.

### `apply_forces(self)`
This is the heart of the physics update.

- During a glide it adds sideways acceleration when A/D is pressed, applies drag so the player slows down when not steering, adds gentle gravity, and subtracts some "lift" proportional to horizontal speed. It limits both horizontal and vertical speeds so the glide stays controllable. If the player stops steering and slows almost to a stop, the code pops the state back to `"airborne"`.
- If the player is not gliding, it simply adds the normal gravity acceleration. In other words, this method decides which physical rules should apply this frame.

### `update_facing(self)`
Looks at the current velocity vector. If the player is moving, the vector is normalised (converted to length 1) and stored in `self.facing`. The drawing code uses this to point the nose triangle so you can see travel direction. When the player is barely moving, the facing vector stays as-is, avoiding random flips.

### `move_and_collide(self, platforms)`
This routine updates positions and handles collisions against the platform list passed in by the game loop.

1. It remembers the previous frame's edges so it can detect "crossing" collisions, which avoids the common problem where fast-moving objects tunnel through the floor.
2. Calls `apply_forces` (described above) to update velocity, then moves vertically, checks for landing or head bumps, and adjusts the position if a platform blocks the movement.
3. Moves horizontally and performs similar checks for left/right wall hits.
4. Finally, it updates the movement state: standing on the ground sets it to `"grounded"`; otherwise, if not gliding, it reverts to `"airborne"`. The method also calls `update_facing` so rendering has a fresh direction vector.

It returns a `ContactInfo` object that summarises what was hit this frame. The rest of the game could read that to trigger animation, sound, or other reactions.

## 4. Putting It Together: A Typical Frame

Here is a simple story of a frame while gliding:

1. You hold the `D` key. `handle_input` stores `self.input_horizontal = 1`.
2. You press space mid-air. `spacebar_event` calls `start_glide`, which boosts the sideways speed, limits the fall speed, and switches to `"gliding"`.
3. The loop calls `move_and_collide`. Inside it, `apply_forces` sees `movement_state == "gliding"`, applies lift and drag, and keeps the glide smooth. After movement, collisions are resolved so you do not clip through platforms.
4. `update_facing` points the nose vector along the new travel direction. The draw code uses that vector to render the triangle in front of the circle.

## 5. Tweaking Tips

- Want the glide to feel floatier? Turn down `GLIDE_GRAVITY` or turn up `GLIDE_LIFT_FACTOR`.
- Need tighter steering? Increase `GLIDE_ACCEL` and maybe `GLIDE_REVERSE_DAMP` so direction changes feel snappier.
- If the glide starts too slowly, raise `GLIDE_MIN_ENTRY_SPEED` or the carry term inside `start_glide`.

Experiment with one constant at a time so you can sense how each slider changes the motion.
