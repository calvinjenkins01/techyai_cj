# X AI-News Autoposter

Automatically finds a trending AI topic (AI news, Claude, ChatGPT, building with AI),
writes a long-form article with Claude, renders a branded header image, and posts it
to your X account every other day.

## How it works

1. **Trending topics** — `src/trending.py` pulls the latest stories from major tech
   RSS feeds (TechCrunch AI, The Verge AI, VentureBeat AI, Ars Technica AI) and ranks
   them by freshness + relevance to your niche keywords (Claude, ChatGPT, AI agents,
   coding tools, etc.). Already-posted stories are skipped via `state.json`.
2. **Article** — `src/generate.py` asks Claude (claude-opus-4-8) to write a hook-first,
   skimmable long-form post (capped at 4,000 chars by default — well under X Premium's
   25,000 limit) plus a headline/subheadline for the image.
3. **Picture** — `src/image.py` renders a 1600x900 branded header card with Pillow.
   No image API or extra cost. Edit `BRAND` and the colors in that file to match your
   account's look.
4. **Post** — `src/post.py` uploads the image and publishes via the official X API.
5. **Schedule** — `.github/workflows/x-autopost.yml` runs daily at 15:00 UTC; the
   script itself enforces the every-other-day cadence (posts only if ≥2 days since
   the last post) and commits `state.json` back so it never double-posts.

## Setup

### 1. X developer account (pay-per-use)

- Create an app at https://developer.x.com (new accounts use pay-per-use pricing:
  ~$0.015 per post — roughly $0.25/month at this cadence).
- Set the app permissions to **Read and Write**, then generate:
  API Key, API Key Secret, Access Token, Access Token Secret.
- **Long-form posts (over 280 chars) require X Premium on the posting account.**
  Without Premium, lower `MAX_POST_CHARS` in `main.py` to 280.
- Per X's rules: mark the account with the **automated account** label
  (X app → Settings → Your account → Account information → Automation).

### 2. Anthropic API key

Get one at https://platform.claude.com. Each article costs a few cents.

### 3. GitHub repository secrets

Add these under Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `X_API_KEY` | X app API key (consumer key) |
| `X_API_SECRET` | X app API key secret |
| `X_ACCESS_TOKEN` | X account access token |
| `X_ACCESS_TOKEN_SECRET` | X account access token secret |

### 4. Test it

Locally (dry run — writes the article and image to `drafts/`, posts nothing):

```bash
cd x-autoposter
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python main.py
```

Review `drafts/`, then publish for real with `python main.py --post --force`.

From GitHub: Actions → "X AI-news autoposter" → Run workflow (check "Dry run"
first to see a draft in the workflow's commit before going live).

## Recommendations

- **Review the first several drafts before trusting full auto.** Run in dry-run mode
  for a week and read what it writes. Fully hands-off AI posting is allowed by X, but
  quality control is what keeps followers.
- Posts every other day is a good cadence for long-form; don't crank it up —
  high-volume automated posting looks like spam to X.
- Tweak the voice in `SYSTEM` inside `src/generate.py` — that's your account's tone.
