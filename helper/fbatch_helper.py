"""
fbatch_helper.py
────────────────
Utility functions for the /fbatch command.
Handles filename parsing, season/quality grouping,
and quality-link message formatting.
"""

import re

# ─── Quality ordering: lowest → highest ───────────────────────────────────────
QUALITY_PRIORITY: dict[str, int] = {
    "360p":   0,
    "480p":   1,
    "540p":   2,
    "720p":   3,
    "1080p":  4,
    "2K":     5,
    "4K":     6,
    "2160p":  6,   # alias for 4K
    "HD":     7,
    "HDRip":  8,
    "BluRay": 9,
    "HEVC":   10,
}

# ─── Fancy unicode display labels ─────────────────────────────────────────────
QUALITY_DISPLAY: dict[str, str] = {
    "360p":   "✧𝟹𝟼𝟶ᴘ✧",
    "480p":   "✧𝟺𝟾𝟶ᴘ✧",
    "540p":   "✧𝟻𝟺𝟶ᴘ✧",
    "720p":   "✧𝟽𝟸𝟶ᴘ✧",
    "1080p":  "✧𝟷𝟶𝟾𝟶ᴘ✧",
    "2K":     "✧𝟸ᴋ✧",
    "4K":     "✧𝟺ᴋ✧",
    "2160p":  "✧𝟺ᴋ✧",
    "HD":     "✧ʜᴅ✧",
    "HDRip":  "✧ʜᴅʀɪᴘ✧",
    "BluRay": "✧ʙʟᴜʀᴀʏ✧",
    "HEVC":   "✧ʜᴇᴠᴄ✧",
}

# ─── Extraction helpers ────────────────────────────────────────────────────────

def extract_quality(filename: str) -> str | None:
    """Return the normalised quality tag found in *filename*, or None."""
    checks = [
        (r'(?i)\b(2160p|4k|uhd)\b',          '4K'),
        (r'(?i)\b(1080p)\b',                  '1080p'),
        (r'(?i)\b(720p)\b',                   '720p'),
        (r'(?i)\b(540p)\b',                   '540p'),
        (r'(?i)\b(480p)\b',                   '480p'),
        (r'(?i)\b(360p)\b',                   '360p'),
        (r'(?i)\b(2k)\b',                     '2K'),
        (r'(?i)\b(hdrip|hdtv)\b',             'HDRip'),
        (r'(?i)\b(blu[-]?ray|bdrip)\b',       'BluRay'),
        (r'(?i)\b(hevc|x265)\b',              'HEVC'),
        (r'(?i)\b(hd)\b',                     'HD'),
    ]
    for pattern, label in checks:
        if re.search(pattern, filename):
            return label
    return None


def extract_season(filename: str) -> str | None:
    """Return the season tag (e.g. 'S01') found in *filename*, or None."""
    match = re.search(r'(?i)(S\d{2})', filename)
    return match.group(1).upper() if match else None


def extract_audio(filename: str) -> str | None:
    """Return the audio-type label found in *filename*, or None."""
    checks = [
        (r'(?i)\b(multi[\s_-]?audio|multi)\b',  'Multi'),
        (r'(?i)\b(dual[\s_-]?audio|dual)\b',    'Dual'),
        (r'(?i)\b(hindi|hin)\b',                 'Hindi'),
        (r'(?i)\b(dubbed|dub)\b',                'Dub'),
        (r'(?i)\b(subbed|sub)\b',                'Sub'),
        (r'(?i)\b(english|eng)\b',               'English'),
        (r'(?i)\b(japanese|jpn)\b',              'Japanese'),
    ]
    for pattern, label in checks:
        if re.search(pattern, filename):
            return label
    return None


def extract_show_title(filename: str) -> str:
    """
    Extract a clean, human-readable show title from *filename*.

    Example
    -------
    'S01_03_The_Klutzy_Class_Monitor_Dual_480p_@ANIME_X_FLEX.mkv'
    → 'The Klutzy Class Monitor'
    """
    name = filename
    # Remove file extension
    name = re.sub(r'\.[a-zA-Z0-9]{2,5}$', '', name)
    # Remove leading S01_03_ / S01E03_ / S01_E03_ style prefix
    name = re.sub(r'(?i)^S\d{2}[_\-\s]?(?:E?\d{2,3}[_\-\s]?)?', '', name)
    # Remove quality tags
    name = re.sub(
        r'(?i)\b(2160p|4k|uhd|1080p|720p|540p|480p|360p|2k|hdrip|hdtv'
        r'|blu[-]?ray|bdrip|hevc|x265|x264|hd|avc|aac|mp4|mkv|h264|h265)\b',
        '', name
    )
    # Remove audio tags
    name = re.sub(
        r'(?i)\b(multi[\s_-]?audio|dual[\s_-]?audio|hindi|dubbed|subbed'
        r'|english|japanese|multi|dual|dub|sub|eng|jpn|hin)\b',
        '', name
    )
    # Remove @channel mentions
    name = re.sub(r'@\S+', '', name)
    # Underscores / hyphens → spaces
    name = re.sub(r'[_\-]+', ' ', name)
    # Collapse whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name.title() if name else "Unknown Show"


# ─── Priority / display helpers ────────────────────────────────────────────────

def get_quality_priority(quality: str) -> int:
    return QUALITY_PRIORITY.get(quality, 99)


def get_quality_display(quality: str) -> str:
    return QUALITY_DISPLAY.get(quality, f"✧{quality}✧")


# ─── Grouping ─────────────────────────────────────────────────────────────────

def group_files_by_season_quality(file_list: list[dict]) -> dict:
    """
    Group *file_list* by season → quality.

    Parameters
    ----------
    file_list : list of dicts with keys ``msg_id``, ``channel_id``, ``filename``

    Returns
    -------
    ``{season: {quality: [file_info, ...]}}``
    """
    grouped: dict[str, dict[str, list]] = {}
    for fi in file_list:
        fname   = fi['filename']
        season  = extract_season(fname)  or "S01"
        quality = extract_quality(fname) or "HD"
        grouped.setdefault(season, {}).setdefault(quality, []).append(fi)
    return grouped


# ─── Message formatting ───────────────────────────────────────────────────────

def build_quality_links_text(season_quality_links: dict) -> str:
    """
    Build the HTML-formatted quality-links panel text sent to the user.

    Parameters
    ----------
    season_quality_links : ``{season: {quality: telegram_url}}``

    Returns
    -------
    HTML string ready to pass to ``send_message(..., parse_mode=ParseMode.HTML)``

    Example output
    --------------
    SEASON: S01 :~
    ✧𝟺𝟾𝟶ᴘ✧ - link | ✧𝟽𝟸𝟶ᴘ✧ - link
                         ✧𝟷𝟶𝟾𝟶ᴘ✧ - link

    SEASON: S02 :~
    ✧𝟺𝟾𝟶ᴘ✧ - link | ✧𝟽𝟸𝟶ᴘ✧ - link
    """
    lines: list[str] = []

    for season in sorted(season_quality_links.keys()):
        lines.append(f"<b>SEASON: {season} :~</b>")

        qualities_sorted = sorted(
            season_quality_links[season].keys(),
            key=get_quality_priority
        )
        pairs: list[str] = []
        for q in qualities_sorted:
            url     = season_quality_links[season][q]
            display = get_quality_display(q)
            pairs.append(f'{display} - <a href="{url}">link</a>')

        # Lay out in rows of 2; a lone last item is indented to look centred
        for i in range(0, len(pairs), 2):
            if i + 1 < len(pairs):
                lines.append(f"{pairs[i]} | {pairs[i + 1]}")
            else:
                lines.append(f" {pairs[i]}")

        lines.append("")   # blank line between seasons

    return "\n".join(lines).strip()


def build_quality_links_text_plain(season_quality_links: dict) -> str:
    """
    Same layout as build_quality_links_text() but returns PLAIN TEXT (no HTML tags).
    Used inside a <code> block so every URL is directly copy-pasteable.
    """
    lines: list[str] = []

    for season in sorted(season_quality_links.keys()):
        lines.append(f"SEASON: {season} :~")

        qualities_sorted = sorted(
            season_quality_links[season].keys(),
            key=get_quality_priority
        )
        pairs: list[str] = []
        for q in qualities_sorted:
            url     = season_quality_links[season][q]
            display = get_quality_display(q)
            pairs.append(f"{display} - {url}")

        for i in range(0, len(pairs), 2):
            if i + 1 < len(pairs):
                lines.append(f"{pairs[i]} | {pairs[i + 1]}")
            else:
                lines.append(f" {pairs[i]}")

        lines.append("")

    return "\n".join(lines).strip()


def build_info_caption(
    show_title: str,
    season: str,
    audio: str | None,
    quality: str,
    episode_count: int,
) -> str:
    """
    Build the caption for the quality-info photo message.

    Parameters
    ----------
    show_title    : cleaned anime / show title
    season        : e.g. "S01"
    audio         : e.g. "Dual", "Sub", or None
    quality       : the single quality for THIS link, e.g. "720p"
    episode_count : number of files / episodes in this quality group
    """
    audio_line   = audio or "N/A"
    quality_line = get_quality_display(quality)

    return (
        f"<blockquote>"
        f"<b>Anime : {show_title}\n"
        f"Season: {season}\n"
        f"Audio: {audio_line}\n"
        f"Quality: {quality_line}\n"
        f"Episodes: {episode_count}</b>"
        f"</blockquote>\n"
        f"<blockquote>≡ Pᴏᴡᴇʀᴇᴅ Bʏ : @BotifyX_Pro_Botz</blockquote>"
    )
