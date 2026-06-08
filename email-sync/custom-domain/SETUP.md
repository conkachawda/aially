# Replace `CEO@…onmicrosoft.com` with a real custom-domain address

The `niteshchawdaconsulting.onmicrosoft.com` part is the **default tenant domain**
Microsoft gives every M365 tenant. You can't rename it, but you **can** add your
own domain (e.g. `niteshchawdaconsulting.com` or `aially.com.au`) and make
`ceo@yourdomain.com` the **primary** address on the same mailbox. The mailbox,
its contents, and the sync all stay exactly the same — only the address changes.

> **Which domain?** I can see you operate **`aially.com.au`** (this repo's site) and
> you recently renewed a domain at **name.com** (likely `niteshchawdaconsulting.com`).
> Pick whichever you want the CEO address on. Tell me the exact domain + where its
> DNS is hosted and I'll give you the precise record values to paste. The steps
> below are the generic procedure.

---

## Step 1 — Add and verify the domain in M365

1. **Microsoft 365 admin center** → **Settings → Domains → Add domain**.
2. Enter `yourdomain.com`.
3. M365 gives you a **TXT verification record** (`MS=msXXXXXXXX`). Add it at your
   DNS host (name.com → *My Domains → DNS Records*), then click **Verify**.

## Step 2 — Add the mail DNS records

At your DNS host, add the records M365 shows you. Typical set:

| Type | Host/Name | Value | Purpose |
|------|-----------|-------|---------|
| MX | `@` | `yourdomain-com.mail.protection.outlook.com` (priority 0) | Inbound mail |
| TXT | `@` | `v=spf1 include:spf.protection.outlook.com -all` | SPF |
| CNAME | `autodiscover` | `autodiscover.outlook.com` | Outlook autoconfig |
| CNAME | `selector1._domainkey` | `selector1-...._domainkey.<tenant>.onmicrosoft.com` | DKIM |
| CNAME | `selector2._domainkey` | `selector2-...._domainkey.<tenant>.onmicrosoft.com` | DKIM |

> **Use the exact values from your own admin center** — the table is the shape, not
> copy-paste-ready values. Enable **DKIM** afterwards under
> *Defender → Email & collaboration → Policies → DKIM*, and consider adding a
> **DMARC** TXT record (`_dmarc` → `v=DMARC1; p=quarantine; …`).

### ⚠️ If you use the domain for a website too (e.g. `aially.com.au` on GitHub Pages)
No conflict. Web records (apex **A** records → GitHub's `185.199.108.153` etc.,
and `www` **CNAME**) and mail records (**MX**, SPF/DKIM **TXT/CNAME**,
`autodiscover` CNAME) are different record types and coexist on the same domain.
Just **don't delete** your existing Pages A/CNAME records when adding the mail ones.

## Step 3 — Make the custom address primary on the CEO mailbox

Once the domain shows **Healthy**:

- **Admin center → Users → Active users →** select the CEO user →
  **Manage username/email** (or **Manage email aliases**).
- Add `ceo@yourdomain.com` as an alias, then **set it as the primary** address.
- Keep `CEO@…onmicrosoft.com` as a secondary alias (don't remove it — it's still
  the account's underlying ID and mail to it will still arrive).

PowerShell equivalent (if you prefer):
```powershell
# Requires the ExchangeOnlineManagement module + Connect-ExchangeOnline
Set-Mailbox -Identity "CEO@niteshchawdaconsulting.onmicrosoft.com" `
  -MicrosoftOnlineServicesID "ceo@yourdomain.com"           # change UPN/sign-in
Set-Mailbox -Identity "ceo@yourdomain.com" `
  -EmailAddresses @{add="smtp:CEO@niteshchawdaconsulting.onmicrosoft.com"} `
  -PrimarySmtpAddress "ceo@yourdomain.com"                  # set primary "From"
```

## Step 4 — Update the sync config (if you changed the sign-in/UPN)

If you changed the **sign-in name (UPN)** to `ceo@yourdomain.com`, update the M365
account in `../mbsync/.mbsyncrc` and re-authorize:
```
User ceo@yourdomain.com
```
```bash
python3 /opt/email-sync/oauth2_token.py --account m365 --authorize
```
If you only added it as an alias and left the UPN as `…onmicrosoft.com`, **no sync
change needed** — keep authenticating with the onmicrosoft UPN; your outgoing
"From" will still show the custom address.

---

## What changes for you, in plain terms

- People email and see **`ceo@yourdomain.com`**.
- Same inbox, same mailbox, same two-way sync — nothing migrates or breaks.
- The `…onmicrosoft.com` address quietly stays as a backup alias.

Send me the domain + DNS host and I'll fill in the exact record values and the
alias commands for your tenant.
