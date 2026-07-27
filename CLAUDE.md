# CJ Content System Rules

## Writing style: ABSOLUTE RULES
- NEVER use dashes of any kind in ANY generated content. This means the hyphen "-",
  the en dash "–", and the em dash "—". Applies to everything: X posts, TikTok and
  Instagram captions, carousel slide text, video scripts, daily text messages,
  articles, image text, and any other content CJ will publish or read.
  Use commas, periods, colons, or reword the sentence instead.
  (Hyphens in code, filenames, and flags are fine. This rule is about content.)

## Brand
- Handle: @techyai_cj (TikTok, Instagram, X)
- Niche: AI news, Claude, ChatGPT, building things with AI
- Signature format: "Things you didn't know" countdown videos
- Content pillars (CJ's chosen four, everything fits one of these):
  1. Things you didn't know (signature discovery countdowns)
  2. AI news with a take (day-of speed, developer perspective)
  3. Technical authority (software developer + cybersecurity angles,
     credibility line "I'm a software developer" in scripts)
  4. How-to workflows (practical AI recipes: exact prompts, settings,
     step by step tasks people can copy)
- Every video ends with a usable takeaway (prompt to copy, setting to
  change, thing to try) plus an engineered CTA (comment bait, send this
  to, or save this)
- Every TikTok and IG caption STARTS with a comment keyword line, e.g.
  Comment "SLIDES" and I'll reply with the exact prompt, then the rest of
  the caption. The keyword must promise something CJ can actually deliver
  (in replies now; via auto DM once the ManyChat funnel exists)
- Two layer hooks: the SPOKEN hook carries the TikTok search phrase; the
  ON SCREEN text is a separate short curiosity line, 4 to 8 words, bold
  claim or curiosity gap, never a descriptive title
- IG captions use only 3 to 4 targeted hashtags (TikTok can carry 4 to 5)
- Daily habit: after replying to own comments, CJ leaves 3 to 5 smart
  comments on bigger AI creator accounts (free discovery)
- Flagship series: "Things you didn't know" gets a fixed weekly slot and
  strict numbering (part 3, part 4, ...) forever; the visible catalog is
  the follow driver. Differentiator vs faceless series accounts: CJ's
  face, developer credential, and same day news speed
- Workflow videos: the exact prompt goes in the caption word for word
  (Prompt 👇 style), copyable text drives saves
- VOICE RULE for every script: write it like CJ is telling ONE friend about
  something he just found, not addressing an audience. Contractions always.
  Short fragments for emphasis. Include at least one real reaction or aside
  ("here's what got me", "no exaggeration", "I wasn't ready for this").
  Casual connectors (so, and, but here's the thing). Banned: influencer
  cliches like "here's what nobody tells you" or "this changes everything",
  press release phrasing, and any sentence CJ wouldn't say out loud to a
  buddy. ALSO BANNED: ellipses and trailing pauses, um/uh, "like" as a
  hedge, and any written-in hesitation. Confident friend, not rambling
  friend: every sentence lands and moves. Test: read it aloud, if it feels
  like reading, rewrite it.
- Every video package Claude delivers includes: script + hook, captions
  (comment keyword first), cover text, YouTube title, rendered vertical
  MP4 overlay clips (CJ stays on camera, clips go over his face), and
  for news videos the source article links to screenshot. Overlay clips
  are rendered with the broll renderer in scratchpad (Pillow + ffmpeg)
- When a good question lands in comments, answer it with TikTok's reply
  with video feature (at least one per week once comments pick up)
- Visual style: terminal aesthetic (default card style "terminal" in x-autoposter,
  matching carousel-maker slides)

## System overview
- daily-sms/: writes today.txt every morning at 4:00am and 5:30am Phoenix
  (11:00 and 12:30 UTC); CJ's iPhone Shortcut fetches it at 6am and texts it
  to him. Update schedule.json every Sunday during the planning session with
  the new week.
- carousel-maker/: renders slide decks for TikTok photo posts + IG carousels.
- x-autoposter/: full X automation (currently off; CJ pastes articles manually).
