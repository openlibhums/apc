# Janeway APC Plugin

A plugin for [Janeway](https://github.com/openlibhums/janeway) that enables journals to set, manage, and track Article Publication Charges (APCs). It supports per-section pricing, invoice lifecycle tracking, fee waivers, discounts, and configurable billing notifications.

**Version:** 1.2

**Minimum Janeway Version:** 1.7.0

**License:** AGPL-3.0

## Features

### Section-Based APC Pricing
Define APC values and currencies per journal section. When an article is submitted, its APC is automatically recorded based on its section's configured rate.

### Invoice Lifecycle Tracking
Track each article's APC through a full status workflow: **New** > **Invoiced** > **Paid** / **Non Payment**. APCs can also be reset back to New if needed.

### Fee Waivers
Authors can apply for APC waivers after submission by providing a rationale. Editors review waiver applications and accept or decline them with a written response. Waiver functionality and the text displayed to authors are both configurable per journal.

### Discounts
Editors can adjust an article's APC value and optionally apply predefined discount templates. All value changes are logged for audit purposes.

### Billing Staff Notifications
Assign staff members to receive email notifications for specific billing events:
- **Ready for Invoicing** -- when an article is accepted
- **Invoice Sent** -- when an APC is marked as invoiced
- **Invoice Paid** -- when an APC is marked as paid
- **Waiver Application** -- when an author submits a waiver request

Notification email templates and subjects are configurable through Janeway's settings system.

### Display Modes
The plugin supports two modes controlled via settings:
- **Enable APCs** -- displays publication fees to authors on the submission page
- **Track APCs** -- tracks charges in the background for journal managers without exposing fee details to authors

### Hooks
The plugin integrates with Janeway's hook system to inject content into three locations:
- `publication_fees` -- renders APC information on the publication fees page
- `submission_review` -- displays waiver policy text during submission review
- `core_article_footer` -- shows a waiver application link on article pages

### Add Articles Manually
Editors can retroactively add accepted articles to APC tracking if they were missed during initial submission (e.g., the plugin was installed after the article was accepted).

## Installation

1. Clone this repo into your Janeway plugins directory:
   ```
   git clone <repo-url> /path/to/janeway/src/plugins/apc
   ```
2. Install the plugin:
   ```
   python3 manage.py install_plugins
   ```
3. Run migrations:
   ```
   python3 manage.py migrate
   ```
4. Restart your web server (Apache, Nginx/Passenger, etc.).

## Configuration

After installation, navigate to the APC plugin settings page in your journal's manager interface to configure:

| Setting | Description |
|---|---|
| **Enable APCs** | Show APC fees to authors during submission |
| **Track APCs** | Track APCs internally without author-facing display |
| **Enable Waivers** | Allow authors to apply for fee waivers |
| **Waiver Text** | Customisable text describing your waiver policy |

You should also set APC values for each journal section from the plugin's main dashboard.

