# liferecorder-website (deploy target)

This repo is the **GitHub Pages deploy target** for https://liferecorderapp.com — do not edit
files here directly. The source of truth is `website/` in the Life Recorder app repo
(Bitbucket `barishshalom/life-recorder`, local `~/Projects/LifeRcorder/website/`).

Deploy = rsync from the source, commit, push (Pages publishes in ~1 min):

```
rsync -a --exclude .git ~/Projects/LifeRcorder/website/ ~/Projects/liferecorder-website/
cd ~/Projects/liferecorder-website && git add -A && git commit -m "…" \
  && git -c credential.helper='!gh auth git-credential' push
```

Custom domain + HTTPS are configured in this repo's Pages settings (CNAME file:
liferecorderapp.com). See `CLAUDE.md` in the app repo for the full operational picture.
