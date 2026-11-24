# liferecorderapp.com (GitHub Pages)

This checkout is the only copy of the site; edit it here. README.md describes an older rsync flow that no longer applies.
Push: `git -c credential.helper='!gh auth git-credential' push` (Pages deploys in about a minute; check it live with curl).
Languages: `index.html` and `get/index.html` are the English sources. `python3 tools/i18n.py` rebuilds the `/<lang>/` and `/<lang>/get/` pages from them; `--check` only checks for missing strings.

## Install links and attribution (2026-11-24)
- **Play** links carry `referrer=utm_source%3Dliferecorderapp.com%26utm_medium%3Dweb%26utm_campaign%3D<placement>`. GA4 shows the attribution on the app's `first_open` (firstUserCampaignName).
- **App Store** links are App Store Connect campaign links: `https://apps.apple.com/app/id6812500586?pt=129464139&ct=<campaign>&mt=8`. `pt` is Bar's provider token. `ct` equals the Play campaign of the same slot: hero/footer/video, `<x>_<lang>` on language pages, and `usecase_*` on use-case pages. The iPhone header/sticky swap takes ct from the Play link it replaces. On redirect pages ct is `C` (get, get_de, share, shareapp, sharetranscript, v). `ct` allows at most 40 characters.
- **App Store campaign data appears only in App Store Connect > Analytics > Acquisition (Campaigns), never in GA4.** GA4 shows every iOS first_open as (direct).
- **/funcallsget** passes the link's own utm through. `?utm_source=funcalls&utm_medium=app&utm_campaign=X` becomes Play referrer `funcalls / app / funcallsget_X` and App Store `ct=funcalls_X` (cut to 40 characters). Unsafe or over-long values fall back to `liferecorderapp.com / web / funcallsget` and `ct=funcallsget`.
- **The redirect pages** (/get + 29 languages, /share, /shareapp, /sharetranscript, /v, /funcallsget) send GA4 by hand with sendBeacon. On these pages `install_click` fires on PAGE LOAD, so it counts landings, not button clicks. `_fv`/`_ss` go on the page_view hit only; until 2026-11-24 both hits sent them, which counted every visitor twice.
- **The home and use-case pages** call `installClick(event, placement)`, which holds navigation until gtag's event_callback runs (400 ms at most).
