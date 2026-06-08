#!/usr/bin/env python3
"""
oauth2_token.py — mint Microsoft OAuth2 access tokens for IMAP (XOAUTH2).

Used by mbsync's PassCmd to authenticate to Outlook.com and Microsoft 365, both
of which require OAuth2 for IMAP (basic auth / app passwords were removed by
Microsoft in 2024).

Stdlib only — no pip installs.

USAGE
-----
  First-time authorization (run once per account, interactively):
      python3 oauth2_token.py --account hotmail --authorize
      python3 oauth2_token.py --account m365    --authorize

  Print a valid access token (what mbsync calls; refreshes silently):
      python3 oauth2_token.py --account hotmail

CONFIG
------
Set your Entra (Azure AD) app client id once (see SETUP.md to register one):
      export MS_OAUTH_CLIENT_ID="00000000-0000-0000-0000-000000000000"

Token cache is written to ~/.config/email-sync/<account>.json (chmod 600).

The same client id works for BOTH a personal Hotmail account and the M365 tenant
mailbox when the app registration allows "any org directory and personal Microsoft
accounts" and "public client flows".
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

# Outlook IMAP scope + offline_access so we get a long-lived refresh token.
SCOPE = "https://outlook.office.com/IMAP.AccessAsUser.All offline_access"
# "common" works for both personal Microsoft accounts and org/tenant accounts.
TENANT = os.environ.get("MS_OAUTH_TENANT", "common")
DEVICECODE_URL = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/devicecode"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"

CONFIG_DIR = os.path.expanduser("~/.config/email-sync")


def _post(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        # Surface the OAuth error payload (e.g. authorization_pending) to caller.
        return json.loads(e.read().decode())


def _cache_path(account):
    return os.path.join(CONFIG_DIR, f"{account}.json")


def _save(account, blob):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    path = _cache_path(account)
    with open(path, "w") as f:
        json.dump(blob, f)
    os.chmod(path, 0o600)


def _load(account):
    try:
        with open(_cache_path(account)) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def _client_id():
    cid = os.environ.get("MS_OAUTH_CLIENT_ID")
    if not cid:
        sys.exit(
            "ERROR: set MS_OAUTH_CLIENT_ID to your Entra app client id "
            "(see SETUP.md)."
        )
    return cid


def authorize(account):
    """Interactive device-code flow. Run once per account."""
    cid = _client_id()
    dc = _post(DEVICECODE_URL, {"client_id": cid, "scope": SCOPE})
    if "user_code" not in dc:
        sys.exit(f"Device code request failed: {dc}")

    print("\n" + "=" * 60, file=sys.stderr)
    print(dc["message"], file=sys.stderr)  # "go to URL and enter CODE"
    print("=" * 60 + "\n", file=sys.stderr)

    interval = int(dc.get("interval", 5))
    deadline = time.time() + int(dc.get("expires_in", 900))
    while time.time() < deadline:
        time.sleep(interval)
        tok = _post(
            TOKEN_URL,
            {
                "client_id": cid,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": dc["device_code"],
            },
        )
        err = tok.get("error")
        if err == "authorization_pending":
            continue
        if err == "slow_down":
            interval += 5
            continue
        if err:
            sys.exit(f"Authorization failed: {tok}")
        # Success.
        tok["expires_at"] = time.time() + int(tok.get("expires_in", 3600))
        _save(account, tok)
        print(f"Authorized '{account}'. Token cached.", file=sys.stderr)
        return
    sys.exit("Device code expired before authorization completed.")


def refresh(account):
    """Use the stored refresh token to get a fresh access token."""
    blob = _load(account)
    if not blob or "refresh_token" not in blob:
        sys.exit(
            f"No token cache for '{account}'. Run with --authorize first."
        )
    cid = _client_id()
    tok = _post(
        TOKEN_URL,
        {
            "client_id": cid,
            "grant_type": "refresh_token",
            "refresh_token": blob["refresh_token"],
            "scope": SCOPE,
        },
    )
    if "access_token" not in tok:
        sys.exit(f"Refresh failed for '{account}': {tok}")
    # Microsoft rotates refresh tokens — keep the newest.
    if "refresh_token" not in tok:
        tok["refresh_token"] = blob["refresh_token"]
    tok["expires_at"] = time.time() + int(tok.get("expires_in", 3600))
    _save(account, tok)
    return tok["access_token"]


def get_token(account):
    """Return a valid access token, refreshing if it expires within 5 min."""
    blob = _load(account)
    if blob and blob.get("access_token") and blob.get("expires_at", 0) > time.time() + 300:
        return blob["access_token"]
    return refresh(account)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--account", required=True, help="e.g. hotmail or m365")
    ap.add_argument(
        "--authorize",
        action="store_true",
        help="run interactive device-code flow (once per account)",
    )
    args = ap.parse_args()

    if args.authorize:
        authorize(args.account)
    else:
        # mbsync reads stdout; print ONLY the token, no trailing junk.
        sys.stdout.write(get_token(args.account))


if __name__ == "__main__":
    main()
