# Email Sync — Hotmail ⇄ Microsoft 365

Two-way ("true mirror") sync between a personal **Outlook.com / Hotmail** account
(`niteshchawda@hotmail.com`) and a **Microsoft 365** tenant mailbox
(`CEO@niteshchawdaconsulting.onmicrosoft.com`).

This folder contains three independent deliverables:

| Folder | What it does | Old mail? | New mail? | Read/flag state? | Needs a server? |
|--------|--------------|-----------|-----------|------------------|-----------------|
| [`mbsync/`](mbsync/) | **Primary engine.** Two-way **copy** of every folder via `mbsync` (isync) with a local Maildir hub — emails show up in both, **nothing is ever deleted**. | ✅ | ✅ | ✅ | Yes — an always-on machine/VPS to run it on a schedule |
| [`power-automate/`](power-automate/) | No-server companion. Cloud flows copy each *new* message both ways. | ❌ (forward-only) | ✅ | ❌ | No |
| [`custom-domain/`](custom-domain/) | Guide to replace the ugly `…onmicrosoft.com` address with a real custom domain (e.g. `ceo@yourdomain.com`). | — | — | — | No |

## Why mbsync is the real answer

There is **no native two-way mailbox sync** between a consumer Outlook.com account
and an M365 tenant mailbox. The old shortcut — Microsoft 365 / Outlook.com
**"Connected Accounts"** — was retired by Microsoft in 2024. Plain two-way
forwarding causes mail loops and syncs nothing useful (no folders, no read state).

`mbsync` is the only approach here that copies your **entire existing mailbox**
(old + new), keeps **folders and read/unread/flag state** in sync, and runs
**both directions**. It is configured **copy-only**: a deletion in one mailbox is
never pushed to the other — emails just show up in both and stay there.

Power Automate is included only as a belt-and-suspenders option for "new mail shows
up in both" with zero infrastructure — but it **cannot backfill old email** and does
not sync read state. Use it *alongside* a one-time mbsync run if you want, not
instead of it.

## How the mirror works (mbsync)

```
  Outlook.com / Hotmail  <--IMAP/OAuth2-->  [ local Maildir hub ]  <--IMAP/OAuth2-->  M365 tenant
        (account A)                          ~/Mail/hub (backup)                       (account B)
```

A shared local Maildir acts as the relay. mbsync keeps per-folder sync state for
each side, so a change made in either account propagates through the hub to the
other. You also get a full local backup of all mail for free.

## ⚠️ Important: this cannot run inside the Claude sandbox

This repo's CI/sandbox is ephemeral and gets wiped — a continuous sync must live on
**your** always-on machine. Everything here is built to be copied out and run there.
Start with [`mbsync/SETUP.md`](mbsync/SETUP.md).
