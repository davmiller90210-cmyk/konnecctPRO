<div align="center" markdown="1">

<a href="https://konnecct.com">
    <img src=".github/logo.svg" height="80" alt="Konnecct logo">
</a>

<h1>Konnecct</h1>

**All-in-one CRM and workspace experience**

_Konnecct is a product fork of [Frappe CRM](https://github.com/frappe/crm), built on the [Frappe Framework](https://github.com/frappe/frappe)._

<div>
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset=".github/screenshots/FrappeCRMHeroImage.png">
        <img width="1402" alt="Konnecct product screenshot" src=".github/screenshots/FrappeCRMHeroImage.png">
    </picture>
</div>

[Website](https://konnecct.com) · [Documentation](https://konnecct.com/docs)

</div>

## Konnecct

Konnecct is an open-source, all-in-one CRM and workspace experience for modern teams. It keeps the same core workflows as upstream Frappe CRM—leads, deals, activities, telephony integrations, and more—while this repository carries Konnecct-specific branding and roadmap.

### Motivation

We want a single product surface that feels cohesive for sales and operations teams, with room to grow beyond classic CRM patterns. The upstream project provides a strong open-source base; Konnecct adapts it for our product direction while remaining compatible with the Frappe ecosystem.

### Key Features

-   **User-Friendly and Flexible:** A simple, intuitive interface that’s easy to navigate and highly customizable, enabling teams to adapt it to their specific processes effortlessly.
-   **All-in-One Lead/Deal Page:** Consolidate all essential actions and details—like activities, comments, notes, tasks, and more—into a single page for a seamless workflow experience.
-   **Kanban View:** Manage leads and deals visually with a drag-and-drop Kanban board, offering clarity and efficiency in tracking progress across stages.
-   **Custom Views:** Design personalized views to organize and display leads and deals using custom filters, sorting, and columns, ensuring quick access to the most relevant information.

    <details>
    <summary>Screenshots</summary>

    <div>
        <picture>
            <source media="(prefers-color-scheme: dark)" srcset=".github/screenshots/LeadList.png">
            <img width="1402" alt="Lead List" src=".github/screenshots/LeadList.png">
        </picture>
    </div>
    <div>
        <picture>
            <source media="(prefers-color-scheme: dark)" srcset=".github/screenshots/LeadPage.png">
            <img width="1402" alt="Lead Page" src=".github/screenshots/LeadPage.png">
        </picture>
    </div>
    <div>
        <picture>
            <source media="(prefers-color-scheme: dark)" srcset=".github/screenshots/EmailTemplate.png">
            <img width="1402" alt="Email Template" src=".github/screenshots/EmailTemplate.png">
        </picture>
    </div>
    <div>
        <picture>
            <source media="(prefers-color-scheme: dark)" srcset=".github/screenshots/CallUI.png">
            <img width="1402" alt="Call UI" src=".github/screenshots/CallUI.png">
        </picture>
    </div>
    <div>
        <picture>
            <source media="(prefers-color-scheme: dark)" srcset=".github/screenshots/CallLog.png">
            <img width="1402" alt="Call Log" src=".github/screenshots/CallLog.png">
        </picture>
    </div>

    </details>

### Integrations

-   **Twilio:** Integrate Twilio to make and receive calls from the CRM. You can also record calls. It is a built-in integration.
-   **Exotel:** Integrate Exotel to make and receive calls via agents mobile phone from the CRM. You can also record calls. It is a built-in integration.
-   **WhatsApp:** Integrate WhatsApp to send and receive messages from the CRM. [Frappe WhatsApp](https://github.com/shridarpatil/frappe_whatsapp) is used for this integration.
-   **ERPNext:** Integrate with [ERPNext](https://erpnext.com) to extend the CRM capabilities to include invoicing, accounting, and more.

### Under the Hood

- [Frappe Framework](https://github.com/frappe/frappe): A full-stack web application framework.
- [Frappe UI](https://github.com/frappe/frappe-ui): A Vue-based UI library, to provide a modern user interface.

### Compatibility
This app is compatible with the following versions of Frappe and ERPNext:

| CRM branch            | Stability | Frappe branch        | ERPNext branch       |
| :-------------------- | :-------- | :------------------- | :------------------- |
| main - v1.x           | stable    | v15.x & v16.x        | v15.x & v16.x        |
| develop - future/v2.x | unstable  | develop - future/v17 | develop - future/v17 |

## Getting Started (Production)

### Production on your own VM (e.g. Google Cloud)

Your fork clone and the running Frappe site are **two different directories**:

| Location | What it is |
|----------|------------|
| `~/konnecctPRO` (or similar) | Git clone of this repository — edit here, commit, push. |
| `~/frappe-bench` (or `bench`’s install path) | Where **`bench`** lives. The app that Frappe actually loads is **`apps/crm`**. |

**Why branding or hooks “don’t apply”:** the server must be running **this** codebase under `frappe-bench/apps/crm` (your fork’s remote and branch, e.g. `develop`), not the default upstream app from `bench get-app crm` without substituting your fork.

**One-time check** (run on the VM; use your real bench path if different):

```bash
cd ~/frappe-bench/apps/crm
git remote -v
git branch --show-current
git log -1 --oneline
```

You should see **your** GitHub fork as `origin` and commits that match this repo (e.g. Website Settings / portal branding changes in `crm/install.py`).

**Deploy updates** (from `~/frappe-bench`, after `git pull` in `apps/crm`):

```bash
bench --site your.site.domain migrate
bench --site your.site.domain clear-cache
bench restart   # if you use supervisor for workers/web
```

Replace `your.site.domain` with your site name (often the same as the public hostname, e.g. `app.konnecct.com`). You can confirm it with `cat sites/currentsite.txt` or `bench use`.

The optional **[docker/](docker/)** Compose setup in this repo is **only** for container-based installs; you do **not** need `cd konnecctPRO/docker` if you use a normal bench on the VM.

#### If the site still says “Frappe”, or signup is still disabled

That means **`frappe-bench/apps/crm` is not this fork**, or **`bench migrate` has not run** on that server since you pulled Konnecct — the running Python code is what updates **Website Settings** in the database.

1. Fix `apps/crm` (fork + `git pull`) and run migrate + clear-cache (commands above).

2. **Force portal settings once** (safe to re-run; from `~/frappe-bench`):

```bash
bench --site your.site.domain execute crm.install.apply_website_portal_settings
bench --site your.site.domain clear-cache
bench restart
```

3. In Desk you can confirm: **Website → Website Settings** — **App Name** should be Konnecct, **Disable signups** unchecked, **Hide footer signup** unchecked.

### Managed Hosting

Get started with your personal or business site with a few clicks on Frappe Cloud - our official hosting service.
<div>
	<a href="https://frappecloud.com/crm/signup" target="_blank">
		<picture>
			<source media="(prefers-color-scheme: dark)" srcset="https://frappe.io/files/try-on-fc-white.png">
			<img src="https://frappe.io/files/try-on-fc-black.png" alt="Try on Frappe Cloud" height="28" />
		</picture>
	</a>
</div>

### Self Hosting

Follow these steps to set up Konnecct in production:

**Step 1**: Download the easy install script

```bash
wget https://frappe.io/easy-install.py
```

**Step 2**: Run the deployment command

```bash
python3 ./easy-install.py deploy \
    --project=crm_prod_setup \
    --email=email.example.com \
    --image=ghcr.io/frappe/crm \
    --version=stable \
    --app=crm \
    --sitename subdomain.domain.tld
```

Replace the following parameters with your values:

-   `email.example.com`: Your email address
-   `subdomain.domain.tld`: Your domain name where CRM will be hosted

The script will set up a production-ready instance of Konnecct with all the necessary configurations in about 5 minutes.

## Getting Started (Development)

### Local Setup

1. [Setup Bench](https://docs.frappe.io/framework/user/en/installation).
1. In the frappe-bench directory, run `bench start` and keep it running.
1. Open a new terminal session and cd into `frappe-bench` directory and run following commands (use **your fork** so you get Konnecct branding and hooks, not only upstream CRM):
    ```sh
    $ bench get-app https://github.com/davmiller90210-cmyk/konnecctPRO.git --branch develop
    $ bench new-site sitename.localhost --install-app crm
    $ bench browse sitename.localhost --user Administrator
    ```
1. Access the crm page at `sitename.localhost:8000/crm` in your web browser.

**For Frontend Development**
1. Open a new terminal session and cd into `frappe-bench/apps/crm`, and run the following commands:
    ```
    yarn install
    yarn dev
    ```
1. Now, you can access the site on vite dev server at `http://sitename.localhost:8080`

**Note:** You'll find Konnecct's frontend inside `frappe-bench/apps/crm/frontend`

### Docker (with free HTTPS via Caddy + Let’s Encrypt)

You need Docker and Docker Compose. See [docker/README.md](docker/README.md) for full detail.

From a clone of this repo:

```bash
cd path/to/konnecctPRO/docker
cp .env.example .env
# Set DOMAIN and SITE_NAME to your real hostname (e.g. app.konnecct.com). DNS must point here first.
docker compose up -d
```

Open **https://YOUR_DOMAIN/crm** — TLS is issued automatically by Caddy. Default login: **Administrator** / **admin**.

## Learn and connect

-   [Telegram Public Group](https://t.me/frappecrm)
-   [Discuss Forum](https://discuss.frappe.io/c/frappe-crm)
-   [Documentation](https://konnecct.com/docs)
-   [YouTube](https://www.youtube.com/@frappetech)
-   [X/Twitter](https://x.com/frappetech)

<br>
<br>
<div align="center" style="padding-top: 0.75rem;">
	<p><small>Built on the <a href="https://frappe.io/framework" target="_blank">Frappe Framework</a> · Upstream: <a href="https://github.com/frappe/crm" target="_blank">Frappe CRM</a></small></p>
</div>
