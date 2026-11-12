# Shonar Bangla RP — client rebrand

Takes the released **SA-MP-Android/App** APK and rebrands it for the
**Shonar Bangla Roleplay** server:

- app name → **Shonar Bangla RP**
- launcher icon → `artwork/icon.png`
- package name is kept (`top.th1nk.samp`) because the native libs hardcode
  `/data/data/top.th1nk.samp/files/` — so the stock app must be **uninstalled**
  before installing this build.

The whole rebrand runs in GitHub Actions (no PC / no phone load).

## Run it

Actions → **Rebrand SBRP client** → *Run workflow* (optionally change the
app name or the base release tag). The signed APK lands in the run's
**Artifacts** as `ShonarBanglaRP-arm64`.

## Layout

    artwork/icon.png        source launcher artwork (1254x1254)
    patch_apk.py            the rebrand script (label + icons + adaptive icon)
    keys/sbrp.jks           stable signing keystore (created on first run)
    .github/workflows/      the CI pipeline

## Signing

A stable keystore is generated once and committed, so later builds install
as **updates** over the previous one (same signature). Keystore password is
in the workflow; this is a personal build, not a Play Store submission.
