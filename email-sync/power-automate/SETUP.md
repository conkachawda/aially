# Power Automate — no-server "copy both ways" companion

This is the **zero-infrastructure** option. Two cloud flows in your Microsoft 365
copy each *new* email from one mailbox into the other, both directions.

> ⚠️ **Read this first.** Power Automate **cannot sync your old/existing email** —
> it only fires on mail that arrives *after* you turn it on. It also does **not**
> sync read/unread state or folder moves. For a true mirror of old + new mail, use
> [`../mbsync`](../mbsync). Use Power Automate only if you want "new mail shows up
> in both inboxes" with nothing to host — and run a **one-time** mbsync (or
> imapsync) pass to backfill the history.

## The loop problem (and the guard)

If Flow A copies Hotmail→M365 and Flow B copies M365→Hotmail, a naive setup will
ping-pong the same message forever. The guard: **stamp every copy** and **skip
anything already stamped.** We use a subject/header marker.

---

## Flow A — Hotmail ➜ M365

1. **portal:** https://make.powerautomate.com → **Create → Automated cloud flow**.
2. **Trigger:** *Outlook.com* connector → **"When a new email arrives (V2)"**,
   signed in as `niteshchawda@hotmail.com`. Folder: **Inbox** (add more flows for
   other folders if needed).
3. **Condition (loop guard):** add a **Condition** →
   `Subject` **does not contain** `[synced]`.
   - Put everything below inside the **If yes** branch.
4. **Action:** *Office 365 Outlook* connector → **"Send an email (V2)"** signed in
   as `CEO@niteshchawdaconsulting.onmicrosoft.com`:
   - **To:** `CEO@niteshchawdaconsulting.onmicrosoft.com`
   - **Subject:** `[synced] @{triggerOutputs()?['body/subject']}`
   - **Body:** `@{triggerOutputs()?['body/body']}`  (set **Is HTML = Yes**)
   - **From (Send as):** leave as the M365 user.
   - Expand **Advanced** → map **Attachments** =
     `@{triggerOutputs()?['body/attachments']}` so files carry over.
5. **Save.** Send yourself a test mail to Hotmail; confirm it appears in M365.

## Flow B — M365 ➜ Hotmail

Mirror image of Flow A:

1. **Trigger:** *Office 365 Outlook* → **"When a new email arrives (V2)"** as
   `CEO@niteshchawdaconsulting.onmicrosoft.com`, folder **Inbox**.
2. **Condition:** `Subject` **does not contain** `[synced]`.
3. **Action:** *Outlook.com* → **"Send an email (V2)"** as
   `niteshchawda@hotmail.com`:
   - **To:** `niteshchawda@hotmail.com`
   - **Subject:** `[synced] @{triggerOutputs()?['body/subject']}`
   - **Body:** `@{triggerOutputs()?['body/body']}` (Is HTML = Yes)
   - map **Attachments** as above.
4. **Save** and test.

---

## Notes & limits

- The `[synced]` prefix is what stops the loop. Don't remove it from the subject
  expressions. (If you dislike the visible prefix, use a custom header marker
  instead — ask me and I'll give the header-based variant.)
- Copies arrive as **new messages from you**, not the original sender — so reply
  addresses won't be the original sender. mbsync does *not* have this problem
  (it mirrors the real messages), which is another reason it's the primary tool.
- Free/most M365 plans include Power Automate for this kind of personal flow;
  premium connectors are **not** required here.
- Forgetting the loop guard on either flow will spam both mailboxes — double-check
  the Condition exists in **both** flows before enabling.
