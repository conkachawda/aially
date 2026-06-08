# Move the CEO mailbox onto `niteshchawda.consulting` → `ceo@niteshchawda.consulting`

The `niteshchawdaconsulting.onmicrosoft.com` part is the **default tenant domain**
Microsoft gives every M365 tenant. You can't rename it, but you **can** add your
own domain **`niteshchawda.consulting`** and make **`ceo@niteshchawda.consulting`**
the **primary** address on the **same** mailbox.

> **Nothing migrates.** It stays the exact same Microsoft 365 account — same inbox,
> same contents, same two-way copy you set up. Only the email address people see
> changes. The old `CEO@niteshchawdaconsulting.onmicrosoft.com` stays on as a
> backup alias and keeps receiving mail.

Concrete values for your tenant are filled in below. The DKIM/MX values follow
Microsoft's standard derivation (dots in the domain become dashes), but **always
confirm against what your own admin center shows** before saving DNS — Microsoft
shows the exact strings to paste.

> **DNS host:** `niteshchawda.consulting`'s DNS is managed at **name.com**. In
> name.com: **My Account → My Domains →** click `niteshchawda.consulting` **→ DNS
> Records** (Manage DNS Records). Leave the **Host** field blank for `@` (root);
> name.com appends the domain automatically. For MX, set **Type=MX**, blank host,
> **Answer** = the `mail.protection.outlook.com` value, **Priority=0**.

> ## ⚠️ Titan email on this domain — read before switching MX
> name.com bundles **Titan Email**. If you currently send/receive
> `ceo@niteshchawda.consulting` (or any address on this domain) through **Titan**,
> note:
> - A domain has **one** live mail provider. Pointing MX at Microsoft 365 means new
>   mail for the domain flows to **M365**, and **Titan stops receiving** it.
> - Mail already sitting in the **Titan** mailbox does **not** move automatically.
>   It can be copied into M365 as a one-time job (the same `oauth2`/IMAP tooling in
>   `../mbsync` can pull Titan → M365 — ask me and I'll add a Titan source).
> - In name.com, **turn off / cancel the Titan email subscription** for this domain
>   once M365 is verified, and **delete the old Titan MX + SPF records** (e.g.
>   `mx1.titan.email`, `mx2.titan.email`, `include:titan.email`) so they don't
>   conflict with the Microsoft ones below.
>
> If the domain is **not** on Titan yet (fresh domain, no live mailboxes), ignore
> this box — it's a clean setup.

---

## Step 1 — Add and verify the domain in M365

1. **Microsoft 365 admin center** → **Settings → Domains → Add domain**.
2. Enter **`niteshchawda.consulting`**.
3. M365 gives you a **TXT verification record** (`MS=msXXXXXXXX`). Add it at your
   DNS host (name.com → *My Domains → DNS Records*), then click **Verify**.

## Step 2 — Add the mail DNS records

At your DNS host, add the records M365 shows you. For `niteshchawda.consulting`
they will be (host names are relative to the domain):

| Type | Host/Name | Value | Purpose |
|------|-----------|-------|---------|
| MX | `@` | `niteshchawda-consulting.mail.protection.outlook.com` (priority 0) | Inbound mail |
| TXT | `@` | `v=spf1 include:spf.protection.outlook.com -all` | SPF |
| CNAME | `autodiscover` | `autodiscover.outlook.com` | Outlook autoconfig |
| CNAME | `selector1._domainkey` | `selector1-niteshchawda-consulting._domainkey.niteshchawdaconsulting.onmicrosoft.com` | DKIM |
| CNAME | `selector2._domainkey` | `selector2-niteshchawda-consulting._domainkey.niteshchawdaconsulting.onmicrosoft.com` | DKIM |

> **Cross-check against your admin center** before saving — the values above are
> the standard derivation but Microsoft shows the authoritative strings (and the
> `MS=…` verification token is unique to you). After verifying, enable **DKIM**
> under *Defender → Email & collaboration → Policies → DKIM*, and consider a
> **DMARC** TXT record (`_dmarc` → `v=DMARC1; p=quarantine; …`).

### If you also point a website at `niteshchawda.consulting`
No conflict. Web records (apex **A** / `www` **CNAME**) and mail records (**MX**,
SPF/DKIM **TXT/CNAME**, `autodiscover` CNAME) are different record types and
coexist on the same domain — just don't delete existing web records when adding
the mail ones. (Your `aially.com.au` GitHub Pages site is a separate domain and
isn't affected either way.)

## Step 3 — Make the custom address primary on the CEO mailbox

Once the domain shows **Healthy**:

- **Admin center → Users → Active users →** select the CEO user →
  **Manage username/email** (or **Manage email aliases**).
- Add `ceo@niteshchawda.consulting` as an alias, then **set it as the primary**
  address.
- Keep `CEO@niteshchawdaconsulting.onmicrosoft.com` as a secondary alias (don't
  remove it — it's still the account's underlying ID and mail to it still arrives).

PowerShell equivalent (if you prefer):
```powershell
# Requires the ExchangeOnlineManagement module + Connect-ExchangeOnline
# (Optional) change the sign-in name / UPN to the custom domain:
Set-Mailbox -Identity "CEO@niteshchawdaconsulting.onmicrosoft.com" `
  -MicrosoftOnlineServicesID "ceo@niteshchawda.consulting"
# Make the custom address the primary "From", keep onmicrosoft as alias:
Set-Mailbox -Identity "ceo@niteshchawda.consulting" `
  -EmailAddresses @{add="smtp:CEO@niteshchawdaconsulting.onmicrosoft.com"} `
  -PrimarySmtpAddress "ceo@niteshchawda.consulting"
```

## Step 4 — Update the sync config (only if you changed the sign-in/UPN)

If you changed the **sign-in name (UPN)** to `ceo@niteshchawda.consulting`, update
the M365 account in `../mbsync/.mbsyncrc` and re-authorize:
```
User ceo@niteshchawda.consulting
```
```bash
python3 /opt/email-sync/oauth2_token.py --account m365 --authorize
```
If you only added it as an alias and left the UPN as
`CEO@niteshchawdaconsulting.onmicrosoft.com`, **no sync change needed** — keep
authenticating with the onmicrosoft UPN; your outgoing "From" still shows
`ceo@niteshchawda.consulting`.

---

## What changes for you, in plain terms

- People email and see **`ceo@niteshchawda.consulting`**.
- Same Microsoft 365 account, same inbox, same two-way copy — nothing migrates or
  breaks.
- `CEO@niteshchawdaconsulting.onmicrosoft.com` quietly stays as a backup alias and
  keeps receiving mail.

Once you confirm `niteshchawda.consulting`'s DNS is at name.com (or tell me where),
I can tailor the exact name.com click-path. The record *values* above are ready to
use as soon as the M365 admin center shows your unique `MS=…` verification token.
