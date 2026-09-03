# 💼 Wellfound Jobs API: A Startup Jobs API for Salary and Equity Data

A startup jobs API for **Wellfound** (formerly AngelList Talent). Search by role, location, and remote status, and get one clean JSON row per job: the full description, **parsed salary and equity** ranges, and the hiring startup's signals including **Y Combinator** backing, top investors, and funding stage.

**Actor:** https://apify.com/johnvc/wellfound-jobs-api?fpr=9n7kx3

## Video Walkthrough

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/0.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

This jobs API turns Wellfound's public startup listings into structured data. You give it `roles` (Wellfound slugs like `software-engineer`, or plain words like "software" and "pm", which are mapped for you) and optionally `locations` such as `san-francisco`, `new-york`, or `london`. Each role and location pair becomes its own search, and the API walks the paginated results for you.

Every row comes back with `title`, `url`, the full markdown `description`, and compensation parsed into real numbers: `salaryMin`, `salaryMax`, `salaryCurrency`, `equityMin`, and `equityMax`. The attached `company` object carries `name`, `size`, `tagline`, `stage`, and the badges Wellfound publishes, so you can keep only **remote startup jobs**, only **YC startup jobs**, or only companies actively hiring.

A concrete use case: set `remoteOnly` with `minSalary` to build a weekly feed of remote startup jobs above a pay floor, then turn on `fetchJobDetails` to add benefits, industry, the company's own website, and geo coordinates for the shortlist you care about.

## Quick Start

### Prerequisites

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) for package management
- An Apify API token. Get your free API key at https://apify.com?fpr=9n7kx3

```bash
git clone https://github.com/johnisanerd/Apify-Wellfound-Jobs-API.git
cd Apify-Wellfound-Jobs-API
uv sync
cp .env.example .env       # then paste your token into .env
uv run python wellfound-jobs-api-example.py
```

### Alternative: set the API key directly

```bash
export APIFY_API_TOKEN="your_apify_api_token_here"
uv run python wellfound-jobs-api-example.py
```

## Why use this Wellfound Jobs API?

- **Full descriptions included.** The complete job description comes back in the listing row, not behind an extra fetch.
- **Salary and equity as numbers.** Wellfound publishes pay as a string like `$135k - $175k * 0.05% - 0.25%`. This API parses it into `salaryMin`, `salaryMax`, `equityMin`, and `equityMax` so you can sort and filter.
- **Startup signals you can filter on.** `ycOnly`, `topInvestorsOnly`, `activelyHiringOnly`, and `companyStage` come straight from the badges Wellfound shows.
- **Pay only for what you get.** Billing is per delivered job, with separate small charges for the description and for optional detail enrichment. Jobs removed by your filters are never charged.

## Features

### Core capabilities

- Search by role, location, and remote status, with automatic pagination
- Free-text role input mapped onto real Wellfound slugs ("software" to `software-engineer`)
- Keyword include and exclude filters over title, description, company, and location
- Salary, equity, job type, and experience filters
- Startup-signal filters: Y Combinator, top investors, actively hiring, funding stage
- Optional detail enrichment: benefits, industry, company website, geo, structured salary
- Paste any Wellfound search URL directly with `startUrls`

### Data quality

- One row per job, deduplicated across every search thread in the run
- ISO timestamps for when each job went live
- Runs that return nothing explain why in the dataset, not just in the log

## Usage examples

### Basic example

```python
run_input = {"roles": ["software-engineer"], "maxItems": 5}
```

### Remote startup jobs

```python
run_input = {"roles": ["software-engineer"], "remoteOnly": True, "maxItems": 25}
```

### YC startup jobs over $150k

```python
run_input = {
    "roles": ["software-engineer"],
    "ycOnly": True,
    "minSalary": 150000,
    "maxItems": 25,
}
```

### Startup jobs in a city, with enrichment

```python
run_input = {
    "roles": ["software-engineer"],
    "locations": ["san-francisco"],
    "fetchJobDetails": True,
    "maxItems": 10,
}
```

## Input parameters

| Parameter | Type | Description |
|---|---|---|
| `roles` | array | Role categories to search. Wellfound slugs or plain words that get mapped ("software" to `software-engineer`). |
| `locations` | array | Location slugs, for example `san-francisco`, `new-york`, `london`, `india`. |
| `remoteOnly` | boolean | Only jobs flagged remote. |
| `keyword` | string | Narrow results to jobs containing this phrase. Wellfound has no site-wide free-text search, so this filters the pages a run fetches. |
| `excludeKeyword` | string | Drop jobs whose title or description contains this phrase. |
| `jobType` | string | `full-time`, `part-time`, `contract`, `internship`. |
| `minSalary` / `maxSalary` | integer | Salary floor and ceiling in USD per year. |
| `minEquity` | integer | Minimum equity grant percent. |
| `ycOnly` | boolean | Only Y Combinator-backed companies. |
| `topInvestorsOnly` | boolean | Only companies flagged as top-investor backed. |
| `activelyHiringOnly` | boolean | Only companies with the actively-hiring badge. |
| `companyStage` | string | Funding stage, for example `early_stage`. |
| `includeDescription` | boolean | Include the full markdown description. Default true. |
| `fetchJobDetails` | boolean | Fetch each job's detail page for extra fields. Default false. |
| `maxItems` | integer | Maximum jobs returned across all searches. |
| `maxPagesPerSearch` | integer | Safety cap on pages per search thread. |
| `startUrls` | array | Paste Wellfound search URLs to scrape directly. |

## Output format

```json
{
  "result_type": "job",
  "id": "4353862",
  "title": "Product Manager",
  "url": "https://wellfound.com/jobs/4353862-product-manager",
  "description": "### About the role ...",
  "compensationRaw": "$130k - $200k * 0.15% - 0.25%",
  "salaryMin": 130000,
  "salaryMax": 200000,
  "salaryCurrency": "USD",
  "equityMin": 0.15,
  "equityMax": 0.25,
  "jobType": "full-time",
  "remote": false,
  "remoteKind": "ONSITE",
  "locationNames": ["San Francisco"],
  "postedAt": "2026-07-28T20:58:57+00:00",
  "company": {
    "name": "Agave API",
    "slug": "agave-api",
    "size": "SIZE_11_50",
    "tagline": "Unified API for construction software",
    "stage": "early_stage",
    "ycFunded": true,
    "topInvestors": true,
    "activelyHiring": true
  }
}
```

With `fetchJobDetails` enabled, rows also carry `benefits`, `industry`, `companyWebsite`, `geo`, `detailSalary`, and `applicantLocationRequirements`.

## Schedule it

Save a task with your search, then attach a [schedule](https://docs.apify.com/platform/schedules) to build a history of new postings. Useful cron strings: `0 7 * * *` for daily at 7 AM, `0 6 * * 1` for Mondays.

## People also search for

**How do I get startup jobs data as an API?** Run this Actor from Python, the Apify API, or any MCP client. It returns JSON, CSV, or Excel.

**How do I find remote startup jobs?** Set `remoteOnly` to true. Rows carry `remote`, `remoteKind`, and `acceptedRemoteLocationNames`.

**How do I find Y Combinator startup jobs?** Set `ycOnly` to true, or filter on `topInvestorsOnly` and `companyStage`.

**Can I get startup jobs for a specific city?** Yes. Combine `roles` with `locations` such as `san-francisco`, `new-york`, or `london`.

**Does it include salary and equity?** Yes, both as raw text and parsed into numeric ranges.

**Is Wellfound free for job seekers?** Yes. This API reads the same public pages a visitor sees and returns them as structured data.

## 🪢 Use this from n8n

This API is available as an n8n community node, **[n8n-nodes-wellfound-jobs-api](https://www.npmjs.com/package/n8n-nodes-wellfound-jobs-api)**. In n8n: **Settings, Community Nodes, Install**, enter `n8n-nodes-wellfound-jobs-api`, accept the risk prompt and restart. The **Wellfound Jobs** node then appears in the node picker, and it works as an AI Agent tool.

---

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the Wellfound Jobs API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/wellfound-jobs-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the Wellfound Jobs API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

---

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/wellfound-jobs-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/wellfound-jobs-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the Wellfound Jobs API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

---

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/wellfound-jobs-api`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/wellfound-jobs-api`, using OAuth when prompted.
5. Ask Claude to run the Wellfound Jobs API.

Open Claude on the web: https://claude.ai/referral/uIlpa7nPLg

---

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/wellfound-jobs-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/wellfound-jobs-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the Wellfound Jobs API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

---

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/wellfound-jobs-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

[**Made with care**](https://apify.com/johnvc?fpr=9n7kx3)

*Use the Wellfound Jobs API to power your recruiting, market research, and lead generation workflows with reliable, structured results.*


Last Updated: 2026.09.03
