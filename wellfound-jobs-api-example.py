"""
Wellfound Jobs API: A Quick Start Example
See more at: https://apify.com/johnvc/wellfound-jobs-api?fpr=9n7kx3
Input schema: https://apify.com/johnvc/wellfound-jobs-api/input-schema?fpr=9n7kx3

This script shows how to call the Wellfound Jobs API on Apify from Python and
read its structured JSON output. It is a startup jobs API for Wellfound
(formerly AngelList Talent): search by role, location, and remote status, and
get one clean row per job with the full description, parsed salary and equity,
and the hiring startup's signals (Y Combinator backing, top investors, funding
stage).

Get your free Apify API key at: https://apify.com?fpr=9n7kx3
"""

import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

# Initialize the Apify client with your API token (read from .env)
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

ACTOR = "johnvc/wellfound-jobs-api"


def show(jobs, label):
    """Print a compact summary of the rows a run returned."""
    print(f"\n=== {label}: {len(jobs)} job(s) ===")
    for job in jobs:
        company = job.get("company") or {}
        salary = ""
        if job.get("salaryMin") is not None:
            cur = job.get("salaryCurrency") or "USD"
            salary = f"  {cur} {int(job['salaryMin']):,} to {int(job['salaryMax']):,}"
        equity = ""
        if job.get("equityMin") is not None:
            equity = f"  equity {job['equityMin']}% to {job['equityMax']}%"
        signals = [s for s in (
            "YC" if company.get("ycFunded") else "",
            "top investors" if company.get("topInvestors") else "",
            company.get("stage") or "",
        ) if s]
        print(f"- {job.get('title')} at {company.get('name')}")
        print(f"    {', '.join(job.get('locationNames') or []) or 'no location listed'}"
              f"{'  remote' if job.get('remote') else ''}{salary}{equity}")
        if signals:
            print(f"    signals: {', '.join(signals)}")
        print(f"    {job.get('url')}")


def fetch(run_input, label):
    """Run the Actor and return only the job rows (skipping any error rows)."""
    run = client.actor(ACTOR).call(run_input=run_input)
    # apify-client 3.x returns a typed Run object, so read the dataset id as an
    # attribute. On the older 2.x client this was a dict (run["defaultDatasetId"]).
    dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())
    for item in items:
        if item.get("result_type") == "error":
            print(f"\n[{label}] {item.get('error_type')}: {item.get('error_message')}")
    jobs = [i for i in items if i.get("result_type") == "job"]
    show(jobs, label)
    return jobs


# --------------------------------------------------------------------------
# 1. Basic search: startup jobs for one role.
#
# Kept small on purpose. maxItems is 5 so your first run stays cheap: you pay
# per job returned, plus a small extra per job when you include the full
# description or turn on detail enrichment. Raise maxItems, add locations, or
# turn on fetchJobDetails to collect more.
#
# `roles` accepts plain words as well as Wellfound slugs: "software" is mapped
# to "software-engineer" for you, "pm" to "product-manager".
# --------------------------------------------------------------------------
fetch({"roles": ["software-engineer"], "maxItems": 5}, "Startup jobs for one role")


# --------------------------------------------------------------------------
# 2. Remote startup jobs.
#
# remoteOnly searches Wellfound's remote role pages. Each row carries `remote`,
# `remoteKind` (for example ONSITE_OR_REMOTE) and `acceptedRemoteLocationNames`,
# so you can tell a fully remote role from a hybrid one and see which countries
# the employer will hire from.
# --------------------------------------------------------------------------
fetch({"roles": ["software-engineer"], "remoteOnly": True, "maxItems": 5},
      "Remote startup jobs")


# --------------------------------------------------------------------------
# 3. Y Combinator startup jobs paying over $150k.
#
# ycOnly keeps only companies carrying Wellfound's Y Combinator badge. The same
# idea works with topInvestorsOnly, activelyHiringOnly, and companyStage.
# Filters are applied before billing, so you are not charged for jobs that are
# filtered out.
# --------------------------------------------------------------------------
fetch({"roles": ["software-engineer"], "ycOnly": True, "minSalary": 150000, "maxItems": 5},
      "YC startup jobs over $150k")


# --------------------------------------------------------------------------
# 4. Startup jobs in a specific city, with detail enrichment.
#
# Each role and location pair becomes its own search. fetchJobDetails adds a
# second request per job to pull structured salary, benefits, industry, the
# company's own website, applicant-location requirements, and geo coordinates.
# It costs an extra event per job, so it is off by default.
# --------------------------------------------------------------------------
enriched = fetch(
    {
        "roles": ["software-engineer"],
        "locations": ["san-francisco"],
        "fetchJobDetails": True,
        "maxItems": 3,
    },
    "Startup jobs in San Francisco, enriched",
)

for job in enriched:
    if job.get("companyWebsite") or job.get("benefits"):
        print(f"\nEnrichment for {job.get('title')}:")
        print(f"  website : {job.get('companyWebsite')}")
        print(f"  industry: {job.get('industry')}")
        print(f"  benefits: {(job.get('benefits') or '')[:120]}")
        print(f"  salary  : {job.get('detailSalary')}")


# --------------------------------------------------------------------------
# 5. Lightweight feed: no descriptions.
#
# Turn includeDescription off for a cheaper listing feed when you only need the
# title, company, compensation and links, for example to populate a job board
# and fetch descriptions later.
# --------------------------------------------------------------------------
fetch({"roles": ["product-manager"], "includeDescription": False, "maxItems": 5},
      "Lightweight listing feed")

print("\nDone. Full field list: https://apify.com/johnvc/wellfound-jobs-api?fpr=9n7kx3")
