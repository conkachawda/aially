# mbsync setup — true two-way mirror (Hotmail ⇄ M365)

End result: every folder in `niteshchawda@hotmail.com` and
`CEO@niteshchawdaconsulting.onmicrosoft.com` stays mirrored in both directions —
**all existing mail and all new mail**, with read/unread and flag state — plus a
local backup. Runs on a schedule on an always-on machine you control.

Budget ~30–45 minutes for first-time setup (mostly the one-time OAuth app
registration). After that it just runs.

---

## 0. What you need

- An **always-on host**: a cheap Linux VPS, a home server, a Raspberry Pi, or a
  Mac/PC that stays on. (Not the Claude sandbox — it gets wiped.)
- Admin access to the **Microsoft 365 tenant** (to enable IMAP and register an app).
- The password / sign-in for the **Hotmail** account.
- `isync` **>= 1.4** (for built-in OAuth2) and Python 3.

```bash
# Debian/Ubuntu
sudo apt install isync python3
# macOS (Homebrew)
brew install isync python3
mbsync --version    # confirm >= 1.4
```

Copy this folder to the host, e.g. `/opt/email-sync`, and:
```bash
chmod +x /opt/email-sync/sync.sh /opt/email-sync/oauth2_token.py
```

---

## 1. Register one Entra (Azure AD) app for OAuth2

Both Outlook.com and M365 require OAuth2 for IMAP now. One app registration covers
both accounts.

1. Go to **https://entra.microsoft.com** → **Identity → Applications → App
   registrations → New registration**.
2. **Name:** `mail-sync` (anything).
3. **Supported account types:** choose
   **"Accounts in any organizational directory and personal Microsoft accounts"**.
   (This is what lets the *same* app authenticate both the tenant mailbox **and**
   the personal Hotmail account.)
4. **Redirect URI:** leave blank. Click **Register**.
5. Copy the **Application (client) ID** — this is your `MS_OAUTH_CLIENT_ID`.
6. **Authentication** (left menu) → **Advanced settings** →
   **Allow public client flows** → **Yes** → Save. (Required for device-code flow.)
7. **API permissions** → **Add a permission** → **APIs my organization uses** →
   search **"Office 365 Exchange Online"** → **Delegated permissions** → add
   **`IMAP.AccessAsUser.All`**. Add **`offline_access`** under Microsoft Graph too
   (for refresh tokens). Click **Grant admin consent** for the tenant.

Set the client id on the host (and in your scheduler — see `schedule.examples`):
```bash
export MS_OAUTH_CLIENT_ID="<the Application (client) ID you copied>"
```

---

## 2. Enable IMAP on the M365 mailbox

IMAP client access must be on for `CEO@niteshchawdaconsulting.onmicrosoft.com`.

- **Microsoft 365 admin center** → **Users → Active users** → select the CEO user →
  **Mail** tab → **Manage email apps** → ensure **IMAP** is checked → Save.

(Outlook.com/Hotmail has IMAP enabled by default — nothing to do there.)

---

## 3. Install the config

```bash
cp /opt/email-sync/.mbsyncrc.template ~/.mbsyncrc
```
Edit `~/.mbsyncrc` and confirm:
- the two `User` lines are correct,
- the `PassCmd` paths point at `/opt/email-sync/oauth2_token.py`.

---

## 4. Authorize each account (one time, interactive)

```bash
python3 /opt/email-sync/oauth2_token.py --account hotmail --authorize
# -> open the URL it prints, sign in as niteshchawda@hotmail.com, enter the code

python3 /opt/email-sync/oauth2_token.py --account m365 --authorize
# -> sign in as CEO@niteshchawdaconsulting.onmicrosoft.com, enter the code
```
Each stores a refresh token in `~/.config/email-sync/<account>.json`. Verify a
token prints:
```bash
python3 /opt/email-sync/oauth2_token.py --account hotmail | head -c 20; echo " ...ok"
```

---

## 5. List folders (sanity check auth + IMAP)

```bash
mbsync --list mirror
```
You should see both accounts' folders (Inbox, Sent Items, Drafts, …). If this
fails, fix auth **before** syncing — see Troubleshooting.

---

## 6. First sync — DO A SAFE PULL FIRST ⚠️

Before letting `Remove/Expunge Both` act, do a non-destructive first pass so a
surprise can't delete mail. Run a **pull-only** initial import once:

```bash
# Pull everything down into the local hub WITHOUT pushing deletes back up.
mbsync --pull-new --pull mirror
```
Inspect `~/Mail/hub/` — confirm both accounts' mail landed. Then run the full
two-way sync:

```bash
/opt/email-sync/sync.sh
tail -n 40 ~/Mail/sync.log
```
The **first full run can take a while** (it copies your entire mailbox history).
Subsequent runs are incremental and fast.

---

## 7. Schedule it

Pick the matching block in [`schedule.examples`](schedule.examples) (cron /
systemd timer / launchd). Every-5-minutes is a good default. Make sure
`MS_OAUTH_CLIENT_ID` is present in the scheduled environment.

---

## How deletes/moves behave

`Create Both`, `Remove Both`, `Expunge Both` make it a true mirror: deleting or
moving a message in **either** account removes/moves it in the other on the next
run. If you'd rather one side never delete from the other, tell me and I'll switch
to a non-destructive profile (`Remove None` on one channel).

---

## Troubleshooting

| Symptom | Fix |
|--------|-----|
| `AUTHENTICATE failed` on M365 | IMAP not enabled (step 2), or admin consent not granted (step 1.7). |
| `AUTHENTICATE failed` on Hotmail | Re-run `--authorize`; ensure account type in the app reg includes **personal Microsoft accounts**. |
| `unsupported mechanism XOAUTH2` | isync too old; need **>= 1.4**. |
| `authorization_pending` loops forever | You didn't finish the device-code sign-in in the browser. |
| Token works manually but cron fails | `MS_OAUTH_CLIENT_ID` missing in the scheduler env (see `schedule.examples`). |
| Throttling / slow on Outlook | Lower `PipelineDepth` in `~/.mbsyncrc` (e.g. 20). |

> Want this folder to never lose mail on a bad run? Ask me to ship the
> "archive-safe" variant (deletes never propagate, only additions/flags).
