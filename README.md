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
1. Open a new terminal session and cd into `frappe-bench` directory and run following commands:
    ```sh
    $ bench get-app crm
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

### Docker

You need Docker, docker-compose and git setup on your machine. Refer [Docker documentation](https://docs.docker.com/). After that, follow below steps:

**Step 1**: Setup folder and download the required files

    mkdir frappe-crm
    cd frappe-crm

    # Download the docker-compose file
    wget -O docker-compose.yml https://raw.githubusercontent.com/frappe/crm/develop/docker/docker-compose.yml

    # Download the setup script
    wget -O init.sh https://raw.githubusercontent.com/frappe/crm/develop/docker/init.sh

**Step 2**: Run the container and daemonize it

    docker compose up -d

**Step 3**: The site [http://crm.localhost:8000/crm](http://crm.localhost:8000/crm) should now be available. The default credentials are:

-   Username: Administrator
-   Password: admin

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
