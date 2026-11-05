# Galatians 6 live slides (wide + vertical, synced)

35 slides, each with a reserved camera area, rendered four ways: `wide/` (1920x1080) and `vert/` (1080x1920) with a linen placeholder (default), and `wide_key/` and `vert_key/` with the slot filled flat chroma green `#00B140` for OBS keying. Files are `01.png`..`35.png` in each folder. The numbers match, so slide 12 in `wide/` and slide 12 in `vert/` are the same moment. The vertical set is laid out for a tall frame (not a crop).

Scripture: **KJV** (public domain), checked word for word against two sources (bible-api.com and helloao eng_kjv). Draft outline, not reviewed by Jonathan yet. No StayTheWay wordmark on any slide.

Colors: natural light set (linen background, forest-green text, olive and sage accents, clay secondary). The earlier dark navy/gold set is kept as `gal6_slides_dark`.

The text is laid out around the camera slot, so nothing sits under it.

Sequence: Title, The Flow, Part 1 "The Read" (7 reading slides with a LISTEN FOR question), Part 2 "Verse by Verse" (3 movements: Carry One Another vv. 1-5, Sow to the Spirit vv. 6-10, Glory in the Cross vv. 11-18, one slide per verse with a QUESTION), Your Move + Say It Out Loud, closing verse (6:9), and the prayer slide ("Text 844-320-PRAY for prayer", staytheway.com).

## Files

| File | What it is |
| --- | --- |
| `index.html` | Launcher. Buttons to open the presenter and the two views, plus a click-to-jump grid of all slides. |
| `presenter.html` | You run this. Current and next slide (wide and vertical), slide number, timer, sync lights. |
| `wide.html` | Fullscreen wide slide, no UI. |
| `vert.html` | Fullscreen vertical slide, no UI. |
| `wide/`, `vert/` | The PNG slides with the placeholder camera area (default). Keep these folders next to the HTML files. |
| `wide_key/`, `vert_key/` | Same slides with the camera area filled with chroma green `#00B140`. Used by `wide.html?key=1` and `vert.html?key=1`. |
| `contact.png` | Contact sheet, all slides, both formats. |
| `src/` | Content, renderer and generator (only needed to change slides). |

No build step, no internet, no dependencies. Open `index.html` by double-click (file) or put the whole folder on any web host.

## Controls (presenter; the wide and vert windows also accept the keys)

- Next: Right arrow, Down arrow, Space, Page Down, Enter, N, or click the slide. Clickers that send Page Down / arrows work.
- Back: Left arrow, Up arrow, Page Up, Backspace, P, or right-click the current slide.
- **B** or **.** toggles black (both windows go black together). Press next/back to leave black.
- Home / End: first / last slide. "Go to" box: jump to a number. F: fullscreen.
- `?key=1` on `wide.html` or `vert.html` shows the green-key set instead of the placeholder set (the presenter has buttons for it). Use it with the OBS Chroma Key filter. Can be combined: `wide.html?key=1&slide=5`.
- `?slide=N`: start at a slide, for example `presenter.html?slide=12`. Opening any of the pages with it moves all the others there too.
- Timer: starts on your first advance. Pause and Reset buttons.
- Sync lights (top right) show green when a wide window and a vert window are open and connected.

## How the sync works

All pages share the current slide through `BroadcastChannel`, with `localStorage` as a fallback (and for pages that open late). Both work for local files and for pages served from a website, as long as **all windows are in the same browser and the same profile** (and the same site/origin if hosted). It does not sync between different browsers or different computers.


## Camera slot (exact pixel coordinates)

The slot is where the camera sat in the Galatians 5 setup, and is the same on every slide in a format. Source: the Gal 5 decks (`StayTheWay_Galatians-5_WIDE.pptx` camera frame, `_VERT.pptx` camera frame) and the Gal 5 edit scripts (`compose.py` overlays the camera at wide x986 y115 878x494; `compose_vert.py` at vertical x22 y840 1037x598). In the Gal 5 live recording the vertical slide sat in the middle of the frame with the camera in its middle band.

Coordinates are in slide pixels, origin top-left. "Outer" includes the 4 px olive border and rounded corners (radius 30 px). "Green interior" is the area inside the border that is flat `#00B140` in the `_key` sets.

| Format | Outer box (x, y, w, h) | Edges (x0,y0 to x1,y1) | Green interior (x, y, w, h) | Position |
| --- | --- | --- | --- | --- |
| Wide 1920x1080 | 986, 115, 878, 494 (16:9) | 986,115 to 1864,609 | 990, 119, 870, 486 | Upper right column, as in Gal 5 |
| Vertical 1080x1920 | 22, 840, 1037, 598 | 22,840 to 1059,1438 | 26, 844, 1029, 590 | Middle band, as in Gal 5 |

As fractions: wide slot x 51.4% to 97.1%, y 10.6% to 56.4%. Vertical slot x 2.0% to 98.1%, y 43.8% to 74.9%.

OBS, exact camera placement: add your camera source, then Edit Transform (Ctrl+E): Positional Type "Bounds", Bounds Type "Scale to outer bounds" (fills the box, crops overflow) or "Scale to inner bounds" (no crop). Use the Green interior column (wide: position 990,119, bounds 870 x 486; vert: position 26,844, bounds 1029 x 590).

OBS, green-key route: put the camera source *below* the slide browser source (`wide.html?key=1`, 1920x1080), add the Chroma Key filter on the browser source with Key Color Type Green or Custom Color `#00B140`, and the camera shows through the slot with the border on top. Same for `vert.html?key=1` at 1080x1920. Or skip keying and place the camera on top using the coordinates above.

StreamYard: layouts are fixed presets, so exact placement is not possible there. For the vertical view, share the vertical window and put the camera in the middle band as in Gal 5. For the wide view, pick a layout with the camera at the upper right and eyeball it to the box, or use OBS for pixel-exact placement.

## Text layout (same as the Galatians 5 deck)

Positions, sizes and alignment are copied from the Gal 5 PowerPoint decks (2 px per point). Colors are the natural palette. Same on every slide type, in pixels:

| Element | Wide 1920x1080 | Vertical 1080x1920 |
| --- | --- | --- |
| Header label ("GALATIANS 6", 26 px bold, left) | x 86, y 65 | x 82, y 89 |
| Chip ("VERSE 3", "READ 1-2", ... 36 px bold) | x 86, y 115, 79 tall | x 82, y 144, 86 tall |
| Counter, right-aligned (26 px: "3 of 18", "Read 2 of 7", "Go do this") | right edge x 1865, y 65 | right edge x 1015, y 170 |
| Gold bar (13 px wide) | x 86, y 238, h 770 | x 82, y 266, h 540 |
| Text box (left aligned, vertically centered, auto-fits down from the Gal 5 size) | x 130, y 238, 806 x 770 | x 125, y 266, 878 x 540 |
| Camera slot | x 986, y 115, 878 x 494 | x 22, y 840, 1037 x 598 |
| Card (label at +36,+43 in 26 px caps; text at +36,+104 in 48 px, auto-fits) | x 986, y 645, 878 x 374 | x 68, y 1466, 945 x 390 |

Start sizes (Gal 5): verse 64 px Georgia bold italic (68 px on the closing verse), reading text 48 px with 40 px verse numbers, title 92 / 84 px, part and divider titles 96 / 88 px, card text 48 px, flow rows 36/40/28 px labels with 36 px italic descriptions, notes 24 px caps, the reference on the closing verse 28 px.

Differences from Gal 5:
- **No wordmark:** Gal 5's "STAYTHEWAY" on the title header, on the closing-verse counter and on its card label is "SUNDAY", removed, and "GALATIANS 6".
- Verse slides show no on-slide reference (Gal 5 did not either; the chip and counter carry it). The closing verse shows it under the quote like Gal 5.
- The Gal 5 title slide has the date on the right. None is shown here because the Gal 6 date is not confirmed.
- The camera frame is a rounded olive border with a placeholder (or green key) instead of Gal 5's dashed gold box.
- Gal 6 adds slide 35 (prayer) in the same structure: chip "NEED PRAYER?", text box, card "ONLINE".

## Use with StreamYard

1. Open `index.html` in Chrome, then click **Open presenter**, **Open wide window**, **Open vertical window**. Keep the presenter on your own screen (do not share it).
2. In StreamYard, add a screen share and pick the **wide window** (Window, then the "Wide" window; or Chrome tab). The slide has a reserved camera area (see Camera slot above), in the same place as Gal 5. StreamYard places the camera by its own layouts, so size it by eye to that box, or use the OBS route for exact placement.
3. Add a second screen share for the **vertical window**, and use it in the portrait layout/destination.
4. Click or press keys in the **presenter** window. Both shares flip together.

Tip: size the windows to the right shape first (wide about 1280x720, vert about 540x960). If you share a browser *tab* instead of a window, Chrome may pause a hidden tab: keep both windows visible, not minimized, or on another desktop that stays rendered. Test with an unlisted live first.

## Use with OBS (browser sources)

1. Add Source, Browser, name "Gal6 Wide": check **Local file** and choose `wide.html` (or enter the hosted URL). Width **1920**, Height **1080**.
2. Add another Browser source, "Gal6 Vert": `vert.html`, Width **1080**, Height **1920** (use it in your vertical canvas, for example with the Aitum Vertical plugin).
3. Run the presenter in a normal browser window or as an OBS custom browser dock (View, Docks, Custom Browser Docks, URL of `presenter.html`). Use the same URL form for all of them (all `file:///` or all `https://same-site`).
4. If the OBS sources and your presenter do not move together, they are not sharing browser storage. Easiest fix: put everything in OBS (presenter as a dock, plus the two browser sources), or right-click a source, Interact, and use the arrow keys there (the keys control every window that is in the same storage).

## Hosting on a website

Upload the whole folder (HTML files, `wide/`, `vert/`) to any folder, for example `staytheway.com/live/gal6/`. Open `presenter.html`, `wide.html`, `vert.html` from that URL in the same browser. This is local-only sync, not a shared one: someone on another computer cannot drive your slides.

## Change a slide

Edit `src/content.py` (text, questions) then run:

```
python3 src/render.py && python3 src/gen_html.py && python3 src/contact.py
```

Needs Python 3 with Pillow and the Gelasio and Inter fonts. Sync test: `src/test_sync.py` (Playwright).

## Notes

- The closing slide says "Text 844-320-PRAY for prayer". The text line was resubmitted to Twilio and is in review; texts stay blocked until it is approved. Skip or hide slide 35 (jump to 34 and press B) until it is approved.
- Slide 17 (v. 5) carries a small note that the Greek uses two different words for "burden" (v. 2, a crushing weight) and "load" (v. 5, a daily pack). Check you want it.
- Questions and key points are a draft; edit to match what you teach.

## Palette (natural light set)

Linen background `#F6F1E3`, sage card `#E3EAD0` (edge `#C8D4AC`), forest text `#1F3326`, description text `#31483A`, olive accent `#4E6B22` (bars, chips, labels), clay secondary `#9A4F2B` (verse references, subtitles, phone number), muted green-gray `#566650` (slide numbers, notes). Text contrast on linen: forest 11.9:1, olive 5.4:1, clay 5.3:1. Change the colors at the top of `src/render.py`.
