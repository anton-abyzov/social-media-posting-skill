#!/usr/bin/env python3
"""
Validate dashboard URLs before showing them to the user.

Usage:
    python3 probe-dashboard-url.py <url> [<url> ...]
    python3 probe-dashboard-url.py --base https://my.blotato.com /posts /schedule /calendar

Output per URL:
    [<status>] <verdict> <url> -> final=<redirect target>
        title=<page title>
        body=<first 80 chars of body>

Verdicts:
    OK          - 200 status and body does not start with "404"
    LOGIN-REDIR - 200 but URL redirected to /login or /auth (route exists, auth-gated)
    404         - body starts with "404" (Next.js apps return 200 + 404 body)
    ERROR       - load failed
"""
import argparse, asyncio, sys
from playwright.async_api import async_playwright


async def probe_one(pw, url):
    browser = await pw.chromium.launch(headless=True)
    ctx = await browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 900},
    )
    page = await ctx.new_page()
    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(1200)
        final = page.url
        status = resp.status if resp else 0
        title = await page.title()
        body = (await page.evaluate("document.body.innerText") or "").strip()
        is_404 = body[:60].strip().startswith("404")
        is_login = "/login" in final or "/auth" in final
        if is_404:
            verdict = "404"
        elif is_login and url not in (final,):
            verdict = "LOGIN-REDIR"
        else:
            verdict = "OK"
        print(f"[{status}] {verdict:11s} {url}")
        print(f"    final: {final}")
        print(f"    title: {title!r}")
        print(f"    body:  {body[:80]!r}")
        return verdict, final
    except Exception as e:
        print(f"[ERR] {url}: {e}")
        return "ERROR", None
    finally:
        await browser.close()


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="Base origin; URLs are joined onto it")
    ap.add_argument("urls", nargs="+", help="Full URLs, or paths if --base is set")
    args = ap.parse_args()

    targets = [
        (args.base.rstrip("/") + u) if args.base and u.startswith("/") else u
        for u in args.urls
    ]
    async with async_playwright() as pw:
        for url in targets:
            await probe_one(pw, url)
            print()


if __name__ == "__main__":
    asyncio.run(main())
