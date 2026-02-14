# X Autoposter

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Set the environment:

```bash
export X_CLIENT_ID="..."
# optional:
export X_CLIENT_SECRET="..."
export X_REDIRECT_URI="http://127.0.0.1:8080/callback"
export NEWS_QUERY="sports"
export HASHTAG="#Sports"
```

A one-time OAuth setup before you get started:

```bash
news2x auth
```

Try a dry run:

```bash
DRY_RUN=1 news2x run
```

Try a real run:

```bash
news2x run
```

This is an example cron job that could run daily at 9:05 AM:

```bash
5 9 * * * cd /path/to/news2x && . .venv/bin/activate && news2x run >> run.log 2>&1
```

### Notes

* This job does 1 post/day (and at most 1 media upload/day).
* Even the published general rate limit table for POST /2/tweets is far above that.
* X is now pay-per-usage and older tiers may differ by account status, so we should confirm in the Developer Console.

### TODO

* Test with client