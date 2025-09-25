# Collision Handling Notes

## Context
The player circle keeps its position and velocity in floats (`pos_x`, `pos_y`, `vel_x`, `vel_y`). The on-screen `pygame.Rect` must use integer coordinates, so each frame we copy the float centre into the rect using `round`. That rounding is why a rect can end up resting perfectly on top of a platform without overlapping it.

## Why `Rect.colliderect` Was Not Enough
`Rect.colliderect` only reports a hit when the rectangles overlap by at least one pixel. When the rounded bottom of the player rect sat exactly on the top of a platform, there was zero overlap, so the collision callback stopped firing. The state machine then flipped between `grounded` and `airborne` every other frame, making jump/glide timing unreliable.

## What the New Checks Do
1. Capture the previous float edges before applying gravity: `prev_bottom` / `prev_top` and their horizontal counterparts.
2. Apply gravity and movement in float space, then check whether the player crossed a platform face this frame:
   - Landing: `vertical_velocity >= 0` AND `prev_bottom <= plat.top` AND `self.rect.bottom >= plat.top`.
   - Head bump: `vertical_velocity < 0` AND `prev_top >= plat.bottom` AND `self.rect.top <= plat.bottom`.
   - Similar logic applies horizontally with left/right edges.
3. When multiple platforms satisfy the condition in the same frame, pick the closest one (highest top for landings, lowest bottom for ceilings, etc.) so list order and big time steps do not matter.
4. Snap the rect to that platform face, reset the relevant velocity component, and update the contact flags.

## Benefits
- Touching a platform now counts as contact because we detect the crossing in float space, before rounding.
- Works for stacked/overlapping platforms and fast movement because we select the nearest candidate instead of "last one processed".
- Keeps the state machine stable regardless of gravity tweaks or sub-pixel positions.

## Code Pointers
- Vertical handling: `game/main.py` lines 70-105.
- Horizontal handling: `game/main.py` lines 111-138.
- Input edge-trigger fix: `game/main.py` lines 178-192.

Keep this note around as a reminder of why the collision logic looks a bit more manual than a plain `Rect.colliderect` call.