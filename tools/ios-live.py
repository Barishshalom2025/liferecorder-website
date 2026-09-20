#!/usr/bin/env python3
"""Turn the whole site's iOS half on (or off) in one command.

  python3 tools/ios-live.py --on     # the day Apple approves
  python3 tools/ios-live.py --off    # put it back
  python3 tools/ios-live.py          # say where things stand

Three mechanical switches, and nothing else:
  1. <html data-ios="0"> -> "1", which reveals every .ios-only badge and button
  2. IOS_LIVE=false -> true on the four redirect pages, so an iPhone tapping a shared clip
     lands in the App Store instead of a "come back later" card
  3. the two visible Android-only labels on the home page

Everything it does NOT touch, it lists: meta descriptions and body copy that still say Android
are a judgement call about search ranking, not a flag.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = sorted(p for p in ROOT.rglob('index.html') if '.git' not in p.parts)
LABELS = [
    ('<span class="tag">Android · Free</span>', '<span class="tag">Android &amp; iPhone · Free</span>'),
    ('Retroactive voice recorder for Android&nbsp;—', 'Retroactive voice recorder for Android &amp; iPhone&nbsp;—'),
    ('<b>Life Recorder</b>Free to download · Android<', '<b>Life Recorder</b>Free to download · Android &amp; iPhone<'),
]


def status():
    # the ATTRIBUTE, not the CSS selectors that read it - counting the string alone reported
    # 8 pages "on" while every one of them was off (2026-09-20)
    on = sum(1 for p in PAGES if 'lang="en" data-ios="1"' in p.read_text(encoding='utf-8'))
    ios_live = sum(1 for p in PAGES if 'var IOS_LIVE=true' in p.read_text(encoding='utf-8'))
    total_flagged = sum(1 for p in PAGES if 'lang="en" data-ios=' in p.read_text(encoding='utf-8'))
    redirects = sum(1 for p in PAGES if 'IOS_LIVE' in p.read_text(encoding='utf-8'))
    print(f'iOS CTAs visible on {on}/{total_flagged} pages | IOS_LIVE true on {ios_live}/{redirects} redirect pages')
    return on, ios_live


def flip(on: bool):
    changed = []
    for p in PAGES:
        s = before = p.read_text(encoding='utf-8')
        # ONLY the <html> attribute: a blanket replace also rewrites the CSS selector that
        # reads it, which inverts the rule and hides everything exactly when it should show
        # (2026-09-20, caught by a screenshot rather than by the code).
        s = s.replace('lang="en" data-ios="0"' if on else 'lang="en" data-ios="1"',
                      'lang="en" data-ios="1"' if on else 'lang="en" data-ios="0"')
        s = s.replace('var IOS_LIVE=false' if on else 'var IOS_LIVE=true',
                      'var IOS_LIVE=true' if on else 'var IOS_LIVE=false')
        for android, both in LABELS:
            s = s.replace(android if on else both, both if on else android)
        if s != before:
            p.write_text(s, encoding='utf-8')
            changed.append(str(p.relative_to(ROOT)))
    print(('switched ON: ' if on else 'switched OFF: ') + f'{len(changed)} page(s)')
    for c in changed:
        print('   ', c)
    # what a flag cannot decide for you
    left = []
    for p in PAGES:
        t = p.read_text(encoding='utf-8')
        for m in re.finditer(r'[^<>]*\bfor Android\b[^<>]*', t):
            left.append(f"{p.relative_to(ROOT)}: …{m.group(0).strip()[:90]}…")
    if left and on:
        print(f'\nstill says Android only ({len(left)} places) - copy, not a switch:')
        for l in left[:8]:
            print('   ', l)
        if len(left) > 8:
            print(f'    … and {len(left)-8} more')


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else '--status'
    if arg == '--on':
        flip(True)
    elif arg == '--off':
        flip(False)
    else:
        status()
