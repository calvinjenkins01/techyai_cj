# Two panel split screen layout, measured from @chase_ai_

Reverse engineered Aug 4 2026 by reading pixels off four of his videos. Use this
when a screen recording has to be legible at phone size, which is the failure
mode on every tutorial video where the recording gets shrunk into a 9:16 frame.

## What the layout actually is
Top panel is the screen, bottom panel is his face, never reversed. Seam sits at
51 to 53 percent of frame height, placed by eye rather than a locked template.
Hard butt join, no gap and no border.

Critical correction to the obvious assumption: the panels are NOT two 16:9 strips
letterboxed with bars. Both sources are scaled up and cropped left and right to
fill the full width. Each panel ends up roughly 1080 x 990, close to square. Text
at the edges of the screen recording gets cut off and he lets it.

The top panel is often a HELD STILL that swaps every 8 to 20 seconds, not a live
recording. Two of the four videos had a top panel that barely moved at all.
That matters: a screenshot that changes at cut points is far less work than a
clean live capture and reads the same.

## CapCut numbers, 1080x1920 canvas, seam at 52 percent
Assumes both sources are 16:9. CapCut treats Scale 100 percent as the clip
fitted inside the canvas, so a 16:9 clip sits at 1080 x 607.5 at 100 percent.

Screen recording, top panel:
  Scale 164 percent, Position X 0, Position Y minus 461

Webcam, bottom panel:
  Scale 152 percent, Position X 0, Position Y plus 499

Clean 50/50 version, both panels 960 tall:
  Both at Scale 158 percent, top Y minus 480, bottom Y plus 480

General formula for any source aspect:
  Scale percent = target panel height divided by (1080 x source height / source
  width), times 100
  Position Y = panel centre row minus 960

Check the sign on Position Y in your build. If the clip moves the wrong
direction, flip it.

## Practical notes
- Frame yourself centred when shooting. The bottom panel crops about 17 percent
  off each side.
- Mute the screen recording, keep the webcam audio as the bed.
- Captions either sit just above the seam overlapping the bottom of the screen
  panel, or deep in the face panel around 76 percent down. Bold white sans,
  heavy black outline, 2 to 4 words per cue, one word in red.
- Full screen breaks are hard cuts with no transition. Split both clips, delete
  one, scale the survivor to fill. Reframe with Position X rather than accepting
  the centre crop.

## When to use it
Use it for tutorials and anything where a screen recording carries the point,
which for CJ means the skills tutorial and the agent build. Do not use it on the
35 second list videos, the panels steal the frame from the hook.
