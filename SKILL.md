---
version: "1.3.1"
name: social-media-posting
description: "One skill for creating, scheduling, posting and replying on social media, with explicit per-post approval. Covers routing (X and TikTok via Blotato, everything else via self-hosted Postiz), account and integration IDs, YouTube channel routing, Postiz/Blotato quirks, clickable preview links, dedup against recent posts, brand-faithful AI visuals (GPT Image 2 for text, Nano Banana Pro for text-free, real logos and real photos as references, 3 options), AI video (Seedance 2.0, veo3_fast fallback), carousels, post-publish verification and daily replies. Platforms: Instagram, LinkedIn, X, Threads, YouTube, TikTok, Facebook, Telegram, Discord, Reddit, dev.to. Use whenever the user wants to post, schedule, cross-post, promote, announce, reply to threads, grow an audience or make social visuals, or names a social platform ('post this', 'share on social', 'schedule on Postiz', 'tweet this', 'quick post', 'post with video')."
repository: anton-abyzov/social-media-posting-skill
metadata:
  tags: social-media, instagram, linkedin, twitter, threads, youtube, tiktok, reddit, discord, telegram, postiz, blotato, posting, engagement, image-generation, video-generation, seedance, brand-fidelity, real-logos
---

# Social Media Posting

Goal: grow Anton's audience and promote his products and personal brand. Copy craft lives in the `copywriting` and `marketing-psychology` skills; video/ad production and Postiz API internals (cookie auth, in-place media swap, >100MB uploads, Instagram covers) live in `postiz-marketing-pipeline`; Kie submit/poll mechanics live in `kie-gemini-omni`.

## Before drafting

1. Read `product-marketing-context.md` (project `.claude/` first, then project root) for brand voice, products and audience. If absent, ask for a one-paragraph brief.
2. Dedup: read the last 10 posts per target platform (Postiz `GET /api/public/v1/posts` for a date window, Blotato `GET /v2/schedules`, or the live profile). If the same topic went out in the last 48h, say so and ask: skip, change angle, or post anyway. Dedup Blotato by (account, caption); `/v2/media` mints a new UUID on every ingest, so media names are useless for dedup. When filtering `/v2/schedules` for TikTok, key the platform as `tiktok`, not `twitter`.
3. Default to Anton's personal accounts. Use brand accounts (EasyChamp, SoothBee, Sketchmate, SkillUp) only when Anton names the brand. Never post brand A content to brand B's channel while brand B is dormant (no post in 30+ days).

## Approval (non-negotiable)

Every post, reply, deletion and replacement needs its own explicit approval in chat before any publish/schedule/delete call.

- One confirmation per platform/account/post. Never batch "approve all".
- Approving a campaign or plan authorizes drafting, not publishing.
- "Looks good", "ok", "sure", a thumbs-up are not approval. Require "publish", "post it to X now" or equivalent; otherwise re-ask.
- Auto mode does not cover posting. A missed schedule is not permission: surface it and ask publish now / reschedule / skip.
- Deleting or replacing a live post gets the same treatment.

Confirmation template (all fields required):

```
Ready to publish:
  Platform: Instagram (@aabyzov)
  Time: now (was 7:00 PM EDT, missed)
  Text: [first 200 chars + "…"]
  Media: 11-slide carousel — URLs below
  Preview: <Postiz /p/<postId> or Blotato /posts URL — after the API call; before it, the dashboard root + the ID to search for>
Reply "publish", "edit" or "skip".
```

Replacement template: `Ready to delete + replace:` with Platform, Currently live `<URL>`, New media, New caption, and `Reply "replace", "edit" or "skip".`

After every successful schedule/publish call, report one block per post with a clickable link and full IDs, never just "scheduled":

```
Scheduled ✓
  Platform: X / Twitter
  Account:  @aabyzov (Blotato accountId 23729)
  Fire at:  2026-05-11 14:30 EDT
  IDs:      scheduleId=978434, postSubmissionId=c4636958-f8c1-4853-9012-f0c051cc01ae
  Manage:   https://my.blotato.com/posts  (Scheduled tab; no per-post deep link)
```

## Preview and live URLs (verified 2026-05-11)

| Surface | Before publish | After publish |
|---|---|---|
| Postiz | `https://postiz.easychamp.com/p/<postId>` — public per-post preview, no login. Secondary: `https://postiz.easychamp.com/launches` calendar (login; for edit/delete). Include `postId` and `group` UUID. | `releaseURL` from `GET /api/public/v1/posts` once `state` is `PUBLISHED` |
| Blotato | `https://my.blotato.com/posts` (Scheduled / Drafts / Published tabs); `https://my.blotato.com/published`. No per-post deep link: `/posts/<id>`, `/schedule`, `/scheduled`, `/dashboard`, `/calendar`, `/queue` all 404; `?id=` survives login but does not filter. | Platform URL (`https://x.com/<handle>/status/<id>`, `https://www.tiktok.com/@<handle>/video/<id>`). Blotato often omits it, so find the post on the profile. |

Before presenting any URL not in this table, probe it with `scripts/probe-dashboard-url.py` (headless Playwright). A redirect to `/login` means the route exists; a 404 status or a body starting with "404" means it does not. Record newly verified URLs here with the date.

## Routing

X/Twitter and TikTok → Blotato. Everything else → Postiz. Postiz's X integration was removed (2026-05-15) and used to fail silently; never route X through it.

### Postiz (self-hosted)

- URL `https://postiz.easychamp.com/api` (Hetzner, Helsinki). Key: `POSTIZ_API_KEY` from the vault note `Postiz creds.md`. Keys from any other Postiz instance return `401 Invalid API key`. Infra runbook: vault note `Postiz on Hetzner.md`.
- Use the `postiz` CLI (`postiz upload`, `postiz posts:create -c ... -m <url> -s <iso> -i <integration>`, `postiz posts:delete`, `postiz integrations:trigger <id> channels`) or the public API `/api/public/v1/posts`.

Personal integration IDs:

| Channel | Integration ID | Handle |
|---|---|---|
| LinkedIn (Anton) | `cmopiw0jb0001outahymxmkhv` | personal |
| Instagram (`instagram-standalone`) | `cmgzh1zr20001pr261ozok9yp` | `aabyzov` |
| YouTube — Anton Abyzov: AI Power | `cmgyq88pu0001po4fdvq4fvii` | `@antonabyzov` |
| YouTube — Abyzov World (family) | `cmq4ojbpe0035ou3kg9hcdrkh` | `@aabyzov` |
| Telegram (Anton AI Power) | `cmoqlxmmc0001ou1tcojd5pps` | `@antonaipower` |
| Discord (EasyChamp server, AI news) | `cmoqm1rui0003ou1tklf1p8pf` | `#ai-news`, channel id `1472307264898728181` |

Also on Postiz (get IDs with `postiz-marketing-pipeline/scripts/postiz-list-channels.sh`): Anton Threads (@aabyzov); EasyChamp YouTube (@easychampinc), Instagram (@easychamp_inc), Facebook page, Discord; SkillUp Football YouTube; Sketchmate IG/FB/YT; SoothBee IG/FB/X/YT/Pinterest (`babyanticry`). Not connected anywhere: Anton's personal Facebook (Postiz handles Pages only), LinkedIn Company Pages, Anton/EasyChamp Pinterest.

**YouTube routing (Anton, 2026-09-09):** anything about, linked to or promoting AI goes to Anton Abyzov: AI Power (`cmgyq88pu0001po4fdvq4fvii`), never to the family channel Abyzov World, even when the subject is Anton's apartment or family. Verify the destination channel before publishing. Short `xyWgiALi3-U` was misrouted to the family channel on 2026-09-05; do not reuse that routing.

Postiz quirks:
- No update. To change a queued post: delete, then recreate (`DELETE /api/public/v1/posts/<postId>` or `postiz posts:delete`). The cookie-auth internal API can update in place; see `postiz-marketing-pipeline`.
- Only QUEUE/DRAFT posts can be deleted. A PUBLISHED post must be removed in the platform's own app. Tell Anton up front that a regenerated visual can supplement a live post, not replace it.
- `state: ERROR` comes back with `error: null, errorMessage: null`; there is no detail.
- Telegram: single `*bold*` asterisks make the post fail silently. Strip them; use at most one image.
- Discord needs `--settings '{"channel":"<channel id>"}'` — the numeric ID, not `#name`. List channels with `postiz integrations:trigger <discord-integration-id> channels`.
- "I see nothing scheduled" in `/launches` while the API shows QUEUE: the Channels sidebar hides personal channels below the brand ones. Tell Anton to toggle them on.

### Blotato

- API `https://backend.blotato.com/v2`, header `blotato-api-key`, key from vault note `Blotato API creds.md` (export as `BLOTATO_API_KEY`).
- Accounts: `GET /v2/users/me/accounts`, or derive from `GET /v2/schedules`. `GET /v2/accounts` returns 401.

| Account | accountId |
|---|---|
| X personal `@aabyzov` | `23729` (was `18001` before the 2026-09 reconnect) |
| X `@EasyChampInc` / `@EasyChampeSport` / `@easychampfcpro` | `18005` / `18007` / `18008` (recorded 2026-05; re-check after the reconnect) |
| TikTok Anton `@antonabyzov` | `40681` |
| TikTok SkillUp `@footballskillup` / EasyChamp `@easychamp_inc` / Sketchmate `@sketchmate.net` / SoothBee `@soothbee` | `41891` / `40691` / `40690` / `40825` |
| LinkedIn Anton (secondary; Postiz is primary) | `20855` |
| X SoothBee/AntiCryBaby `@anticry52675` / Sketchmate `@sketchmateai` / SkillUp `@skillupfootball` / JobWeave `@jobweaveai` | `18476` / `19033` / `19558` / `18924` (audit 2026-05-27; re-check via `GET /v2/users/me/accounts` after the 2026-09 reconnect) |
| TikTok JobWeave `@jobweaveai` | `43482` (same caveat) |

X limits for standard non-Premium accounts (`@aabyzov` is not Premium): 280 weighted chars (a URL counts as 23, so a 279-raw-char caption can fail), video at most 120s; render at or under 118.8s and preflight with `ffprobe -show_entries format=duration`. `@EasyChampeSport` (18007) has accepted captions over 280 chars (vault note). If a business X account is missing from `GET /v2/users/me/accounts`, ask Anton to add it in the Blotato dashboard before posting.

Text limits elsewhere: Threads 500, LinkedIn 3,000, Discord 2,000, Telegram 4,096, Instagram/TikTok captions 2,200.

Post (tweet; for a thread add `"additionalPosts": [{"text": "..."}]`, up to 10, each may carry its own `mediaUrls`; max 20 media per tweet):

```json
{
  "post": {
    "accountId": "23729",
    "content": {"text": "Tweet text", "mediaUrls": ["<Blotato CDN url>"], "platform": "twitter"},
    "target": {"targetType": "twitter"}
  },
  "scheduledTime": "2026-05-11T18:30:00Z"
}
```

`POST /v2/posts`; omit `scheduledTime` to publish now. TikTok: `platform`/`targetType` `tiktok`; video is one URL in `mediaUrls`; a photo carousel is several URLs plus `target.imageCoverIndex: 0`.

- Media handoff: `postiz upload <file>` → Postiz CDN URL → `POST /v2/media {"url": ...}` → put the returned Blotato URL in `mediaUrls`.
- To change a schedule: `DELETE /v2/schedules/<scheduleId>` and recreate. `scheduleId` is not the `postSubmissionId`; find it in `GET /v2/schedules` by accountId + scheduledTime. Keep both IDs: scheduleId for delete, postSubmissionId for status.
- Scheduled posts fire on real wall-clock time; a long render can miss early slots.

### Not on Postiz or Blotato

Reddit has no API route here: draft the post and let Anton publish it, or drive the browser only with his per-post approval (gotchas below). dev.to can go through Postiz.

## Visuals

### Models (Kie `https://api.kie.ai/api/v1/jobs/createTask`; mechanics in `kie-gemini-omni`)

- Any frame with readable text (slides, posters, covers): `gpt-image-2-text-to-image`, or `gpt-image-2-image-to-image` with reference URLs in `input_urls`.
- Text-free hero/atmosphere shots: `nano-banana-pro`, references in `image_input` (up to 14 URLs).
- Video: `bytedance/seedance-2` (Seedance 2.0): 1080p, 4–15s, native audio. Use either `first_frame_url` + `last_frame_url` (narrative arc: make start and end frames with GPT Image 2, then prompt the transition) or `reference_image_urls` (style/character consistency); the two modes are mutually exclusive. Fallback when speed matters: `veo3_fast`.
- References must be public URLs. Upload local files with `postiz upload <file>` first.
- Make 3 distinct options per image and let Anton pick. Generate at the target ratio; never upscale or crop an AI image afterwards.

Ratios: Instagram feed 4:5 (1080x1350) by default; every slide in a carousel has the same ratio; Instagram accepts 0.8–1.91, at least 320px on the shortest side (aim for 1080px) and at most 8 MB per image. Other image caps: X 5 MB (16:9, 1200x675); YouTube thumbnail 2 MB (16:9, 1280x720); dev.to cover 1 MB (1000x420); LinkedIn/Facebook/Threads/Discord 8 MB; Telegram 10 MB; TikTok 20 MB. TikTok/Reels/Shorts 9:16. Pad user screenshots to fit (blurred or solid background); never crop them.

### Real brands and logos

Never let a generator invent a logo. A hallucinated logo means regenerate.

1. Find the real logo, in this order: local brand kits (`~/Pictures`, `~/Desktop`, `~/Documents/logos`, project `assets/`, `.claude/brand/`), the Obsidian vault (`003 Resources/`), Wikimedia Commons direct URLs, the brand's own portal, then `logos-world.net`. Avoid `cdn.brandfetch.io` (needs auth, returns HTML) and random image search.
2. Confirm with `file <path>` that it is a real PNG/SVG/JPEG, at least 512px on the long edge.
3. Pass the logos as references and name them in the prompt ("the OpenAI logo (image 1) on the left"), with: *"Use the supplied reference images verbatim — do not stylize the logos, do not invent shapes, render them photorealistically as real brand assets. Logos must be pixel-accurate to the references."*
4. Default style: photorealistic editorial / studio product render. Do not use "abstract", "stylized", "ethereal", "glowing neon logos", "non-Euclidean" or "logo reimagined as"; they produce fake logos.
5. Zoom in on every logo (or ask a vision model) and regenerate anything off before showing Anton.

Verified logo URLs (add a row each time a new brand is researched):

| Brand | URL |
|---|---|
| Microsoft | `https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/1280px-Microsoft_logo.svg.png` |
| Microsoft Azure | `https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Microsoft_Azure_Logo.svg/1280px-Microsoft_Azure_Logo.svg.png` |
| OpenAI | `https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/OpenAI_Logo.svg/1280px-OpenAI_Logo.svg.png` |
| AWS | `https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Amazon_Web_Services_Logo.svg/1280px-Amazon_Web_Services_Logo.svg.png` |
| xAI | `https://logos-world.net/wp-content/uploads/2023/07/xAI-Logo.png` |
| Anthropic (A\ symbol, 256x256) | `https://cdn.prod.website-files.com/67ce28cfec624e2b733f8a52/67d31dd7aa394792257596c5_webclip.png` |

Do not use the Anthropic wordmark SVG (`https://upload.wikimedia.org/wikipedia/commons/7/78/Anthropic_logo.svg`): at carousel sizes its slanted I reads "ANTHROP\C". Pass the A\ symbol and write "Anthropic" as plain text in the prompt.

### Real people

Never let a generator invent a real person's face. Fetch a real photo and pass it as a reference with: *"Use the supplied reference photograph verbatim — preserve their actual face, do not stylize, do not invent features. The person in the rendered image must be visually identifiable as the real public figure."*

Use direct Wikimedia file URLs, `https://upload.wikimedia.org/wikipedia/commons/<a>/<bc>/<File_Name>.jpg`. `thumb/` paths return HTML to Kie's servers and fail silently. Check with `file` before use. Verified (add rows as you go):

| Person | URL |
|---|---|
| Sam Altman | `https://upload.wikimedia.org/wikipedia/commons/2/2f/Sam_Altman_speaking_at_TED_%28cropped%29.jpg` |
| Satya Nadella | `https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg` |
| Elon Musk | `https://upload.wikimedia.org/wikipedia/commons/3/34/Elon_Musk_Royal_Society_%28crop2%29.jpg` |
| Dario Amodei | `https://upload.wikimedia.org/wikipedia/commons/9/9e/Dario_Amodei_in_2023.jpg` |

For athletes and anything promotional, follow the rights rules in `postiz-marketing-pipeline` (CC-licensed photos with attribution, never an AI-generated real face).

### Proof first

On X and Threads, image 1 is a real proof screenshot (terminal output, dashboard number, before/after) whenever one exists; AI art comes second. Ask Anton for one if the topic has none. Never fabricate a screenshot.

### Carousels (Instagram, TikTok)

Default to 8–12 slides for dense stories: hook (slide 1, the only one most people see) → context (1–2) → conflict → resolution → optional video slide → one "Who is X" slide per key entity (real logo plus 4 facts of 5–8 words; write the name as plain text) → specific CTA. Generate each slide as its own GPT Image 2 call and open every prompt with the same style clause, adapting only the ratio:

> *"Editorial 1:1 Instagram-carousel slide, photorealistic, hyperreal IMAX cinematography, magazine cover quality. BIG bold sans-serif headline at top. All text rendered crisply."*

For video, the first frame has to stop the scroll: no fade-in or black opening, and a user-supplied asset goes first. YouTube and TikTok always get a custom thumbnail. When the same video goes to several platforms, post to YouTube on day 0, TikTok on day 2–3 and Instagram Reels on day 3–4.

## Platform failure points

- **Instagram caption drop.** When Anton asks for "text and an image", ask whether the text goes in the caption or on the slides, then make sure it lands somewhere. Never publish with an empty caption when copy was written. Don't repeat slide text in the caption. Instagram video covers: set `thumbnailTimestamp` (see `postiz-marketing-pipeline`).
- **X media.** Media must be a Blotato CDN URL in `mediaUrls` (via the handoff above). After it fires, open the tweet and confirm the image or video rendered. A post that went out without the media Anton asked for is a failure: report it, don't call it done.
- **TikTok.** Before re-posting anything, check `tiktok.com/@<handle>` to see whether the first attempt went live.

## Browser fallback gotchas

Use only when Postiz/Blotato fail or for Reddit, and still only with per-post approval. Learned the hard way:

- **Keyboard layout.** Anton's Mac often has the Russian input source active. An AppleScript `Cmd+Shift+G` "Go to Folder" path typed under a non-Latin layout turns to garbage and nothing attaches, with no error. Switch to an English source (`U.S.`/`ABC`) via `osascript` + System Events, wait 0.3s, type the path, press Enter, then restore the original source. Check with `osascript -e 'tell application "System Events" to return name of current input source'`. Telegram's picker also needs ~2s between AppleScript steps.
- **Clipboard text.** CDP `Input.insertText` corrupts text in X and Threads editors, and shell `printf … | pbcopy` mangles UTF-8 (`—` → `‚Äî`). Copy with Python, `subprocess.Popen(['pbcopy']).communicate(text.encode('utf-8'))`, then `cliclick kd:cmd t:v ku:cmd`.
- **TikTok Studio.** Override `navigator.webdriver` before page load and make no CDP calls during upload. Convert photo carousels to video first (ffmpeg `-preset slow -crf 18 -movflags +faststart`, 1080x1920, at least 16s). The DraftJS caption ignores paste; use Playwright `type`. The Post button sits below the fold: `scrollIntoView({block:'center'})`, recompute coordinates, then `cliclick`. `webmssdk` answers `{code: 7, Permission Denied}` when CDP is attached; the video is already uploaded, so ask Anton to click Post himself. The page gives no success signal: check `tiktok.com/@<handle>` in a separate tab (wait ~10s) before any retry.
- **Threads.** Type the caption before attaching (focus changes clear the file input). Wait for `div[role="dialog"] img[src*="blob:"]` before posting; no preview means no image. A text match on `Post` hits the feed-header button or "Add to thread" first, so click the Post button via an aria-ref snapshot scoped to the compose dialog.
- **X.** Wait for the attachment preview (`[data-testid="attachments"] img`) before `tweetButtonInline`. If `setFileInputFiles` is rejected, use CDP `DOM.setFileInputFiles` on the node's backendNodeId; for video, wait 45s after it before clicking Post.
- **Telegram web.** The caption field is `.form-control.allow-selection`, not a normal contenteditable, so insertText fails: focus it and paste via Python pbcopy + Cmd+V. Enter adds a newline, it does not send; find the Send button by `textContent.trim() === 'Send'`. Clicking the message area first opens the emoji picker instead of attachments: Escape, then click the paperclip.
- **YouTube Studio.** After setting `textContent` on a contenteditable metadata field, dispatch an `input` event or it won't save.
- **Instagram private API.** `Transcode not finished`: wait 30s after the video upload before `configure_to_clips`. `cover_photo_upload_error`: upload the cover via `rupload_igphoto` with the same `upload_id` before configure. The caption goes in the `configure` call, not the upload call. An expired `sessionid` cookie means Anton re-logs in Chrome.

## Verify and log

Open the live URL, take a headless screenshot, and check that: (a) the text has no encoding damage (`‚Äî`, `â€œ`, `Ã©`, stray Cyrillic); (b) the image, video or first slide is present and correct. Report the URL with what you found. Never call an unverified post a success. Append the post URLs and asset paths to `post-history/YYYY-MM-DD-<topic>.md`.

## Daily engagement

For each platform, find 10 active threads on Anton's topics and draft one reply each: 1–3 sentences that add something new, in a human tone, with no em dashes and self-promotion in at most 1–2 of the 10. Present the drafts together, but post only the ones Anton approves explicitly, by number. Rate limits: Reddit max 3 comments per thread per hour and 5 per 30 minutes, 5–10 minutes apart; X max 5 replies per 10 minutes; LinkedIn 5–7 comments per hour. Stop on any CAPTCHA or rate limit and report it. After posting and engagement, log posts, replies and links to `memory/YYYY-MM-DD-engagement-log.md`.
