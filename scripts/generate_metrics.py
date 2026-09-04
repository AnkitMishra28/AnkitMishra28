#!/usr/bin/env python3
"""
generate_metrics.py
Safely generates and refreshes static GitHub profile metric SVGs.

Validates that any downloaded or generated content is a legitimate,
error-free SVG before writing to disk. If a rate limit or API error
occurs, existing valid SVG files are preserved so the profile never displays
broken images or rate-limit warnings.
"""

import os
import sys
import time
import urllib.request
import urllib.error

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
USERNAME = "AnkitMishra28"

CARDS = [
    {
        "target": "profile/github-stats.svg",
        "urls": [
            f"https://github-stats-extended.vercel.app/api?username={USERNAME}&show_icons=true&theme=tokyonight&hide_border=true",
            f"https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=tokyonight&hide_border=true",
        ],
        "description": "GitHub Activity & Repository Statistics",
    },
    {
        "target": "profile/github-streak.svg",
        "urls": [
            f"https://github-readme-streak-stats.herokuapp.com/?user={USERNAME}&theme=tokyonight&hide_border=true",
        ],
        "description": "GitHub Contribution Streak",
    },
    {
        "target": "profile-summary-card-output/tokyonight/0-profile-details.svg",
        "urls": [
            f"https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username={USERNAME}&theme=tokyonight",
        ],
        "description": "Profile Details & 12-Month Contribution Trend",
    },
    {
        "target": "profile-summary-card-output/tokyonight/1-repos-per-language.svg",
        "urls": [
            f"https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username={USERNAME}&theme=tokyonight",
        ],
        "description": "Top Languages by Repository Count",
    },
    {
        "target": "profile-summary-card-output/tokyonight/2-most-commit-language.svg",
        "urls": [
            f"https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username={USERNAME}&theme=tokyonight",
        ],
        "description": "Top Languages by Commit Volume",
    },
    {
        "target": "profile-summary-card-output/tokyonight/3-stats.svg",
        "urls": [
            f"https://github-profile-summary-cards.vercel.app/api/cards/stats?username={USERNAME}&theme=tokyonight",
        ],
        "description": "Profile Summary Stats",
    },
    {
        "target": "profile-summary-card-output/tokyonight/4-productive-time.svg",
        "urls": [
            f"https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username={USERNAME}&theme=tokyonight&utcOffset=5.5",
        ],
        "description": "Productive Coding Time (Asia/Kolkata UTC+5.5)",
    },
]


def validate_svg(content: str) -> bool:
    """Verify that the fetched content is a valid, error-free SVG."""
    if not content or len(content) < 500:
        return False
    lower = content.lower()
    if "<svg" not in lower or "</svg>" not in lower:
        return False
    error_indicators = [
        "error!!!",
        "temporarily rate limited",
        "rate limit",
        "something went wrong",
        "service unavailable",
        "502 bad gateway",
        "503 service",
    ]
    for err in error_indicators:
        if err in lower:
            return False
    return True


def fetch_card(target: str, urls: list, description: str) -> bool:
    """Fetch card content from primary or fallback URLs with retry."""
    print(f"[{description}] Processing {target}...")
    headers = {"User-Agent": USER_AGENT}

    for url in urls:
        for attempt in range(1, 4):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=25) as resp:
                    if resp.status != 200:
                        print(f"  Attempt {attempt} returned status {resp.status} for {url}")
                        time.sleep(2)
                        continue
                    content = resp.read().decode("utf-8", errors="replace")
                    if validate_svg(content):
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                        with open(target, "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"  [OK] Successfully updated {target} ({len(content)} bytes)")
                        return True
                    else:
                        print(f"  Attempt {attempt} content failed validation (possible rate limit / error SVG)")
            except urllib.error.HTTPError as e:
                print(f"  HTTP error {e.code} on attempt {attempt}: {e.reason}")
            except Exception as e:
                print(f"  Error on attempt {attempt}: {e}")
            time.sleep(2)

    if os.path.exists(target):
        print(f"  [WARN] Maintained existing valid file: {target}")
        return True
    else:
        print(f"  [FAIL] Failed to generate and no existing file found for: {target}")
        return False


def main():
    print("Starting GitHub Profile Metrics Generation...")
    all_ok = True
    for card in CARDS:
        ok = fetch_card(card["target"], card["urls"], card["description"])
        if not ok:
            all_ok = False

    if not all_ok:
        print("ERROR: One or more critical metric cards could not be generated.")
        sys.exit(1)
    print("All metrics generated and validated successfully.")


if __name__ == "__main__":
    main()
