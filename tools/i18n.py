#!/usr/bin/env python3
"""Build the translated home page and /get page for every app language.

index.html and get/index.html stay the ENGLISH SOURCE. This script reads them, swaps every
English string listed in tools/i18n/en.json for the same key in tools/i18n/<lang>.json, and
writes /<lang>/index.html + /<lang>/get/index.html. It also (re)writes the hreflang block and
the footer language list into the English page, the sitemap's home-page entries, and the
per-language screenshots (assets/i18n/<lang>-*.webp, from the app repo's framed Play shots).

  python3 tools/i18n.py            # build everything
  python3 tools/i18n.py --check    # fail if an English string is missing from the source
  python3 tools/i18n.py --images   # also re-convert the screenshots (after a retake)

Edit English copy in index.html AND en.json together; a key whose English no longer matches
the page makes --check fail, so a translated page never silently keeps old English.
"""
import json, os, re, sys, html

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = os.path.join(SITE, 'tools', 'i18n')
SHOTS = os.path.expanduser('~/Projects/LifeRecorder/Liferecorder App/store-assets/screenshots/locales')
BASE = 'https://liferecorderapp.com'

# site folder -> (hreflang, Play screenshot locale, Google Play badge code, rtl)
LANGS = {
    'ar': ('ar', 'ar', 'ar', True), 'cs': ('cs', 'cs-CZ', 'cs', False),
    'da': ('da', 'da-DK', 'da', False), 'de': ('de', 'de-DE', 'de', False),
    'el': ('el', 'el-GR', 'el', False), 'es': ('es', 'es-ES', 'es', False),
    'fi': ('fi', 'fi-FI', 'fi', False), 'fil': ('fil', 'fil', 'fil', False),
    'fr': ('fr', 'fr-FR', 'fr', False), 'he': ('he', 'iw-IL', 'iw', True),
    'hi': ('hi', 'hi-IN', 'hi', False), 'hu': ('hu', 'hu-HU', 'hu', False),
    'id': ('id', 'id', 'id', False), 'it': ('it', 'it-IT', 'it', False),
    'ja': ('ja', 'ja-JP', 'ja', False), 'ko': ('ko', 'ko-KR', 'ko', False),
    'ms': ('ms', 'ms', 'ms', False), 'nb': ('nb', 'no-NO', 'no', False),
    'nl': ('nl', 'nl-NL', 'nl', False), 'pl': ('pl', 'pl-PL', 'pl', False),
    'pt': ('pt-BR', 'pt-BR', 'pt-br', False), 'ro': ('ro', 'ro', 'ro', False),
    'ru': ('ru', 'ru-RU', 'ru', False), 'sv': ('sv', 'sv-SE', 'sv', False),
    'th': ('th', 'th', 'th', False), 'tr': ('tr', 'tr-TR', 'tr', False),
    'uk': ('uk', 'uk', 'uk', False), 'vi': ('vi', 'vi', 'vi', False),
    'zh': ('zh-Hans', 'zh-CN', 'zh-cn', False),
}
# Screenshots shown per page: hero + the three in "Inside the app" (Play framed file names).
SHOT_FILES = {'record': '01_02_recorder_recording_framed.png', 'playing': '03_04_playing_framed.png',
              'trim': '04_05_trim_framed.png'}
# Google serves a localized "Get it on Google Play" badge only for some codes; the rest
# fall back to English (checked by HTTP 200 when this was written, 2026-11-23).
BADGE_OK_FILE = os.path.join(I18N, 'badges-ok.json')

FONT_STACK = ('-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,'
              '"Noto Sans","Noto Sans Arabic","Noto Sans Hebrew","Noto Sans Devanagari",'
              '"Noto Sans Thai","Hiragino Sans","Noto Sans JP","Apple SD Gothic Neo","Noto Sans KR",'
              '"PingFang SC","Noto Sans SC",sans-serif')

START, END = '<!-- i18n:start -->', '<!-- i18n:end -->'
RTL_CSS = ('[dir=rtl] .wave{transform:scaleX(-1)}'
           '[dir=rtl] header nav,[dir=rtl] footer .links,[dir=rtl] .installbar .btn-install{margin-left:0;margin-right:auto}'
           '[dir=rtl] .hero{text-align:right}'
           '[dir=rtl] .fact{border-left:0;border-right:3px solid var(--end);border-radius:12px 0 0 12px}')
FSTART, FEND = '<!-- i18n-switch:start -->', '<!-- i18n-switch:end -->'


def load(lang):
    return json.load(open(os.path.join(I18N, lang + '.json'), encoding='utf-8'))


def flex(text):
    """A regex for English text whatever its line breaks and indentation are in the page."""
    parts = re.split(r'\s+', text.strip())
    return re.compile(r'\s+'.join(re.escape(p) for p in parts))


def names():
    out = {'en': 'English'}
    for l in LANGS:
        f = os.path.join(I18N, l + '.json')
        out[l] = load(l)['lang_name'] if os.path.exists(f) else l
    return out


def head_block(page):
    """hreflang links for the home page (page='') - /get is noindex and gets none."""
    lines = [START]
    lines.append(f'<link rel="alternate" hreflang="en" href="{BASE}/{page}">')
    for l, (code, *_r) in LANGS.items():
        lines.append(f'<link rel="alternate" hreflang="{code}" href="{BASE}/{l}/{page}">')
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/{page}">')
    lines.append(END)
    return '\n'.join(lines)


def switcher(current, label):
    nm = names()
    items = ['<a href="/" hreflang="en" lang="en"%s>English</a>' % (' aria-current="page"' if current == 'en' else '')]
    for l, (code, *_r) in LANGS.items():
        cur = ' aria-current="page"' if l == current else ''
        items.append(f'<a href="/{l}/" hreflang="{code}" lang="{code}"{cur}>{html.escape(nm[l])}</a>')
    return (f'{FSTART}\n<details class="langs"><summary>🌐 {html.escape(label)}</summary>'
            f'<div class="langs-list">{"".join(items)}</div></details>\n{FEND}')


SWITCH_CSS = ('.langs{margin-top:14px;width:100%}.langs summary{cursor:pointer;color:var(--dim);font-size:14px;'
              'list-style:none}.langs summary::-webkit-details-marker{display:none}'
              '.langs-list{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:10px;font-size:14px}'
              '.langs-list a[aria-current]{color:var(--text);font-weight:600}')


def place(src, block, a, b, anchor, before=True):
    """Replace the a..b block, or insert it next to anchor the first time."""
    if a in src:
        return re.sub(re.escape(a) + r'.*?' + re.escape(b), lambda m: block, src, flags=re.S)
    i = src.index(anchor)
    return src[:i] + block + '\n' + src[i:] if before else src[:i + len(anchor)] + '\n' + block + src[i + len(anchor):]


def english_page():
    """Put the hreflang block + language list into the English source page itself."""
    p = os.path.join(SITE, 'index.html')
    s = open(p, encoding='utf-8').read()
    s = place(s, head_block(''), START, END, '<meta name="theme-color"')
    s = place(s, switcher('en', 'English'), FSTART, FEND, '  </div>\n</footer>')
    if '.langs{' not in s:
        s = s.replace('</style>', SWITCH_CSS + '\n</style>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    return s


def absolutize(s):
    """Pages under /<lang>/ need site-root links where the English page had relative ones."""
    return re.sub(r'((?:href|src)=")(?!https?:|#|mailto:|/|liferecorder:|data:)', r'\1/', s)


def faq_ld(t):
    q = [{'@type': 'Question', 'name': t[f'q{i}'],
          'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'<[^>]+>', '', t[f'a{i}'])}} for i in range(1, 8)]
    return ('<script type="application/ld+json">\n' +
            json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': q}, ensure_ascii=False) +
            '\n</script>')


PROTECT = re.compile(r'(<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->)', re.S)


def rx_for(text):
    """English text as a regex: any whitespace run matches any whitespace run; short strings
    must be a whole element text (>FAQ<), longer ones a whole attribute value or text run."""
    body = flex(text).pattern
    if len(text) <= 14:
        return re.compile(r'(?<=>)' + body + r'(?=<)')
    return re.compile(r'(?<=[>"\s])' + body + r'(?=[<"\s&])')


def translate(src, en, t, lang, check_only=False):
    """Swap every English string outside scripts, styles and comments."""
    keys = [k for k in en if not (k.startswith('_') or k == 'lang_name' or k.startswith('get_'))]
    keys.sort(key=lambda k: -len(en[k]))
    parts = PROTECT.split(src)
    found = set()
    for k in keys:
        rx = rx_for(en[k])
        for i in range(0, len(parts), 2):
            if rx.search(parts[i]):
                found.add(k)
                if not check_only:
                    val = t.get(k)
                    if val is None:
                        sys.exit(f'{lang}: key {k} missing')
                    parts[i] = rx.sub(lambda m: val, parts[i])
    return ''.join(parts), [k for k in keys if k not in found]


def build_home(lang, en, src_en, badges):
    t = load(lang)
    code, shot_loc, badge, rtl = LANGS[lang]
    s = src_en
    # The English FAQ JSON-LD is rebuilt from the translations (quotes inside answers would
    # break a string swap in JSON).
    s = re.sub(r'<script type="application/ld\+json">\s*\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>',
               lambda m: faq_ld(t), s, count=1, flags=re.S)
    s, missing = translate(s, en, t, lang)
    if missing:
        sys.exit(f'{lang}: English not found in the page for keys {missing}')
    s = absolutize(s)
    s = s.replace('<html lang="en" data-ios="1">',
                  f'<html lang="{code}" data-ios="1"' + (' dir="rtl"' if rtl else '') + '>', 1)
    s = s.replace(f'<link rel="canonical" href="{BASE}/">', f'<link rel="canonical" href="{BASE}/{lang}/">', 1)
    s = s.replace(f'<meta property="og:url" content="{BASE}/">',
                  f'<meta property="og:url" content="{BASE}/{lang}/">\n<meta property="og:locale" content="{code.replace("-", "_")}">', 1)
    s = place(s, head_block(''), START, END, '<meta name="theme-color"')
    s = place(s, switcher(lang, t['lang_name']), FSTART, FEND, '  </div>\n</footer>')
    # Localized screenshots.
    s = s.replace('/assets/life-recorder-android-record-save-last-minutes.webp', f'/assets/i18n/{lang}-record.webp')
    s = s.replace('/assets/life-recorder-recordings-waveform-player.webp', f'/assets/i18n/{lang}-playing.webp')
    s = s.replace('/assets/life-recorder-trim-audio-live-waveform.webp', f'/assets/i18n/{lang}-trim.webp')
    s = s.replace('width="640" height="1138"', 'width="640" height="1138"')
    if badge in badges:
        s = s.replace('/intl/en_us/badges/static/images/badges/en_badge_web_generic.png',
                      f'/intl/en_us/badges/static/images/badges/{badge}_badge_web_generic.png')
    # Placements carry the language so GA4 (placement is registered; dims are full) splits them.
    def tag(name):  # hero -> hero_de, hero_ios -> hero_de_ios (the iOS header swap appends _ios too)
        return name[:-4] + f'_{lang}_ios' if name.endswith('_ios') else f'{name}_{lang}'
    s = re.sub(r"installClick\(event,'([a-z_]+)'\)", lambda m: f"installClick(event,'{tag(m.group(1))}')", s)
    s = s.replace("m[1].slice(-4)!==\"_ios\"", "m[1].indexOf(\"_ios\")<0")
    s = re.sub(r'utm_campaign%3D([a-z_]+)', lambda m: f'utm_campaign%3D{m.group(1)}_{lang}', s)
    s = re.sub(r'&amp;ct=([a-z_]+)&amp;mt=8', lambda m: f'&amp;ct={m.group(1)}_{lang}&amp;mt=8', s)  # App Store campaign = Play campaign
    s = re.sub(r'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif',
               'font-family:' + FONT_STACK, s, count=1)
    if rtl:
        s = s.replace('</style>', RTL_CSS + '\n</style>', 1)
    out = os.path.join(SITE, lang, 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)


def build_get(lang, en, src):
    t = load(lang)
    code, _s, _b, rtl = LANGS[lang]
    s = src
    s = s.replace('<html lang="en" data-ios="1">', f'<html lang="{code}" data-ios="1"' + (' dir="rtl"' if rtl else '') + '>', 1)
    s = s.replace('var C="get";', f'var C="get_{lang}";', 1)
    s = s.replace('utm_campaign%3Dget"', f'utm_campaign%3Dget_{lang}"', 1)
    js = lambda v: html.escape(v, quote=False).replace("\\", "\\\\").replace("'", "\\'")
    swaps = [  # (English, translation, inside a single-quoted JS string?)
        ('<title>Life Recorder — Get it on Google Play</title>', f'<title>Life Recorder — {html.escape(t["get_gp"])}</title>', False),
        ('<p>Taking you to the store…</p>', '<p>' + html.escape(t['get_taking']) + '</p>', False),
        ('<p class="code">Your invite code<br>', '<p class="code">' + js(t['get_code']) + '<br>', True),
        ('>Open the app with my code</a>', '>' + js(t['get_open']) + '</a>', True),
        ('>Download on the App Store</a>', '>' + js(t['get_as']) + '</a>', True),
        ('>Get it on Google Play</a>', '>' + js(t['get_gp']) + '</a>', True),
        ('<p class="tag">Save the moment after it happened.</p>', '<p class="tag">' + js(t['get_tag']) + '</p>', True),
        ('New here? Download first, then come back and tap open - the code applies itself.', js(t['get_new']), True),
        ('Life Recorder is coming to iPhone shortly - your code stays valid.', js(t['get_soon']), True),
    ]
    for a, b, _in_js in swaps:
        if a not in s:
            sys.exit(f'get page: "{a}" not found')
        s = s.replace(a, b)
    out = os.path.join(SITE, lang, 'get', 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(s)


def images():
    from PIL import Image
    os.makedirs(os.path.join(SITE, 'assets', 'i18n'), exist_ok=True)
    for lang, (_c, loc, _b, _r) in LANGS.items():
        for key, name in SHOT_FILES.items():
            im = Image.open(os.path.join(SHOTS, loc, 'framed', name)).convert('RGB').resize((640, 1138), Image.LANCZOS)
            im.save(os.path.join(SITE, 'assets', 'i18n', f'{lang}-{key}.webp'), 'WEBP', quality=78, method=6)


def sitemap():
    p = os.path.join(SITE, 'sitemap.xml')
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'\s*<url><loc>https://liferecorderapp.com/[a-z]{2,3}/</loc>.*?</url>', '', s)
    if 'xmlns:xhtml' not in s:
        s = s.replace('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
                      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">')
    alts = (f'<xhtml:link rel="alternate" hreflang="en" href="{BASE}/"/>' +
            ''.join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{BASE}/{l}/"/>' for l, (c, *_r) in LANGS.items()) +
            f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}/"/>')
    s = re.sub(r'(<url><loc>https://liferecorderapp.com/</loc>)(?:<xhtml:link[^>]*/>)*', lambda m: m.group(1) + alts, s, count=1)
    rows = ''.join(f'\n  <url><loc>{BASE}/{l}/</loc>{alts}<lastmod>2026-11-23</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>'
                   for l in LANGS)
    s = s.replace('\n</urlset>', rows + '\n</urlset>')
    open(p, 'w', encoding='utf-8').write(s)


def main():
    en = load('en')
    src = open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()
    _, missing = translate(src, en, en, 'en', check_only=True)
    if missing:
        sys.exit(f'English page lacks keys {missing}')
    if '--check' in sys.argv:
        print('ok'); return
    if '--images' in sys.argv or not os.path.isdir(os.path.join(SITE, 'assets', 'i18n')):
        images()
    badges = set(json.load(open(BADGE_OK_FILE))) if os.path.exists(BADGE_OK_FILE) else set()
    src = english_page()
    get_src = open(os.path.join(SITE, 'get', 'index.html'), encoding='utf-8').read()
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else list(LANGS)
    for lang in only:
        build_home(lang, en, src, badges)
        build_get(lang, en, get_src)
    sitemap()
    print(f'built {len(LANGS)} languages x 2 pages')


if __name__ == '__main__':
    main()
