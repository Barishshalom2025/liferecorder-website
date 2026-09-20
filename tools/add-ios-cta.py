#!/usr/bin/env python3
"""Add the App Store call to action beside every Google Play one, hidden until iOS is live.

Every page that offers the app offered it on Android only. This puts Apple's badge and a
matching button next to Play's, wherever Play appears, and hides them behind `data-ios="0"`
on <html> so the site stays truthful while the App Store build is in review. One command
reveals them all: tools/ios-live.py --on

Run once. It is idempotent: a page that already carries the iOS markup is skipped.
"""
import pathlib, re, sys

APP_STORE = 'https://apps.apple.com/app/id6812500586'
ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ('[data-ios="0"] .ios-only{display:none!important}'
       '.badge-ios img{height:48px;display:block}'
       '.badge-ios{display:inline-flex;align-items:center;min-height:64px}')


def badge_html(placement, depth):
    src = ('../' * depth) + 'assets/download-on-the-app-store.svg' if depth else 'assets/download-on-the-app-store.svg'
    return (f'\n        <a class="badge badge-ios ios-only" href="{APP_STORE}" '
            f'onclick="installClick(event,\'{placement}_ios\')">'
            f'<img alt="Download on the App Store" src="{src}" width="143" height="48"></a>')


def button_html(placement):
    return (f'\n    <a class="btn-install ios-only" href="{APP_STORE}" '
            f'onclick="installClick(event,\'{placement}_ios\')">Install free on the App&nbsp;Store</a>')


def main():
    pages = sorted(p for p in ROOT.rglob('index.html') if '.git' not in p.parts)
    pages += [ROOT / 'index.html'] if (ROOT / 'index.html') not in pages else []
    touched = 0
    for page in pages:
        s = page.read_text(encoding='utf-8')
        if 'play.google.com/store/apps/details' not in s or 'badge-ios' in s:
            continue
        depth = len(page.relative_to(ROOT).parts) - 1
        # 1. the flag lives on <html>, so one attribute hides or shows every iOS element
        s = s.replace('<html lang="en">', '<html lang="en" data-ios="0">', 1)
        # 2. the rules that hide them, appended to the page's own stylesheet
        s = re.sub(r'(\n</style>)', CSS + r'\1', s, count=1)
        # 3. a badge after each Play badge, and a button after each Play button
        def after_badge(m):
            placement = re.search(r"installClick\(event,'([^']+)'\)", m.group(0))
            return m.group(0) + badge_html(placement.group(1) if placement else 'cta', depth)
        s = re.sub(r'<a class="badge" href="https://play\.google\.com[^>]*>.*?</a>', after_badge, s, flags=re.S)

        def after_button(m):
            placement = re.search(r"installClick\(event,'([^']+)'\)", m.group(0))
            return m.group(0) + button_html(placement.group(1) if placement else 'cta')
        s = re.sub(r'<a class="btn-install" href="https://play\.google\.com[^>]*>[^<]*</a>', after_button, s)
        page.write_text(s, encoding='utf-8')
        touched += 1
        print(f'  {page.relative_to(ROOT)}: {s.count("badge-ios")} badge(s), '
              f'{s.count("btn-install ios-only")} button(s)')
    print(f'{touched} page(s) updated; all iOS elements hidden until tools/ios-live.py --on')


if __name__ == '__main__':
    main()
