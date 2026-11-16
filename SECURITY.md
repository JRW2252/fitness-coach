# Security Policy

This repository is a public collection of coaching instructions (Markdown), a tracker layout, and, in some branches, helper scripts that talk to third-party services such as intervals.icu. It holds no user accounts or servers. The security risks that matter most here are leaked credentials, leaked personal training or health data, and scripts that handle API keys unsafely.

## Supported versions

Only the `main` branch is supported. Fixes land on `main`; there are no versioned releases or backports.

## Reporting a vulnerability

Please report privately, not in a public issue or pull request.

1. Go to the repository's **Security** tab and choose **Report a vulnerability** (GitHub private vulnerability reporting).
2. If that option is not available, open a public issue that says only "I have a security report, please enable a private channel". Do not include details, keys, or personal data in it.

Helpful details: what you found, where (file and line), how to reproduce it, and the impact you expect. Please do not test against accounts or data that are not yours.

You can expect an acknowledgement within about 7 days and a fix or a decision within about 30 days. This is a small project maintained by an individual, so these are targets, not guarantees. Reporters who want credit will be named in the fix unless they ask otherwise.

## In scope

- Credentials in the repo or its history: API keys, tokens, athlete ids, machine or Zwift folder ids, passwords
- Personal data committed by mistake: training or readiness logs, `state.json`, health details, email addresses
- Scripts (such as `workout-sync/scripts/intervals_icu.py`) that could expose a key, for instance through command-line arguments, logs, or error messages, or that send data somewhere unexpected
- Workflows or dependencies that could run untrusted code

## Out of scope

- The correctness of the training or health guidance. This is coaching information, not medical advice. If you think a recommendation is unsafe, please open a normal issue or pull request.
- Vulnerabilities in Zwift, intervals.icu, GitHub, or any AI model you use with these files. Report those to the vendor.
- Reports that need physical access to someone's computer or a compromised account.

## If you accidentally commit a secret

1. Revoke or rotate the key immediately (for intervals.icu: Settings > Developer Settings). Removing it from the repo is not enough, because it stays in git history and in any forks.
2. Then remove it from the repository, and tell the maintainer if the history needs to be rewritten.

## Guidance for contributors and users

- Keep API keys in environment variables, never in files in this repo. Do not print or log them.
- Keep `state.json`, `logs/`, and anything with real athlete data out of the repo (use a `.gitignore`; an example is in `workout-sync/gitignore.example`).
- Use placeholders in examples (athlete id `0`, FTP 250, `<ZWIFT_USER_ID>`).
- Do not paste secrets or medical records into prompts for AI models you do not control.
- Review any script before running it, especially ones that make network requests.
