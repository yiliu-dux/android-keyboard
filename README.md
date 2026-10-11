### Fork changes

- update encoding for windows android studio
- un-rounded action button
- expanded resizing limits
- made horizontal/vertical spacing between keys uniform
- fix emoji and emoji search window spacing
- add chinese input fuzzy pinyin
- use [rime-ice](https://github.com/iDvel/rime-ice) for Simplified full pinyin when it is present in the imported Chinese dictionary (falls back to `luna_pinyin_simp`)

#### Packing the rime-ice dictionary

`tools/pack_rime_ice.py` builds an importable Chinese dictionary from a rime-ice clone (using its Lua-free schemas, as the bundled librime has no Lua plugin) on top of an existing FUTO Chinese dictionary zip (for Traditional, stroke and OpenCC data):

```
git clone https://github.com/iDvel/rime-ice
python tools/pack_rime_ice.py --rime-ice ../rime-ice --base ../zidian-v26.02.dict --out rime-ice-zh.zip
```

- Add `--include-tencent` to also include the large Tencent word list (much slower first-time deployment on the phone).
- Add `--name "..."` to set the dictionary name shown in the app. Importing a different name triggers re-extraction.
- **Rename the output from `.zip` to `.dict`** (e.g. `rime-ice-zh.dict`), then import that file in FUTO Keyboard.


# FUTO Keyboard

The goal is to make a good modern keyboard that stays offline and doesn't spy on you. This keyboard is a fork of [LatinIME, The Android Open-Source Keyboard](https://android.googlesource.com/platform/packages/inputmethods/LatinIME), with significant changes made to it.

Check out the [FUTO Keyboard website](https://keyboard.futo.tech/) for downloads and more information.

The code is licensed under the [FUTO Source First License 1.1](LICENSE.md).

## Issue tracking and contributing

Please check the GitHub repository to report issues: [https://github.com/futo-org/android-keyboard/](https://github.com/futo-org/android-keyboard/)

The source code is hosted on our [internal GitLab](https://gitlab.futo.org/keyboard/latinime) and mirrored to [GitHub](https://github.com/futo-org/android-keyboard/). As registration is closed on our internal GitLab, we use GitHub instead for issues and pull requests.

If you want to help translate the app, please do so via our Pontoon instance: https://i18n-keyboard.futo.org/

Due to custom license, pull requests to this repository require signing a [CLA](https://cla.futo.org/) which you can do after opening a PR. Contributions to the [layouts repo](https://github.com/futo-org/futo-keyboard-layouts) don't require CLA as they're Apache-2.0

Please do not submit AI-generated pull requests, as these tend to make the codebase more difficult to understand. Pull requests made with clear heavy use of AI may be closed without comment. Please also avoid using AI to write issues, and try to explain it in your own words instead.

## Layouts

If you want to contribute layouts, check out the [layouts repo](https://github.com/futo-org/futo-keyboard-layouts).

## Building

When cloning the repository, you must perform a recursive clone to fetch all dependencies:
```
git clone --recursive https://gitlab.futo.org/keyboard/latinime.git
```

If you forgot to specify recursive clone, use this to fetch submodules:
```
git submodule update --init --recursive
```

You can then open the project in Android Studio and build it that way, or use gradle commands:
```
./gradlew assembleUnstableDebug
./gradlew assembleStableRelease
```

## APK signing

For official FUTO Keyboard versions, you can verify the APK's signing key fingerprint for integrity.

```
Signing key fingerprint for all versions except Google Play:

MD5: 3A:BB:71:C6:BB:E4:92:27:B1:E3:5D:81:01:48:6A:B0
SHA1: 5D:15:B3:6E:C9:6A:96:28:41:09:DD:62:93:0D:9C:39:9F:5F:06:43
SHA-256: 74:3F:AD:58:64:AB:C4:26:50:0B:2D:C2:C4:7C:8A:D3:24:CB:CD:16:03:3F:80:16:99:48:41:35:63:74:F9:95

```
