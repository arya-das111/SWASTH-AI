# Security Policy

## Supported Versions

This project is currently in active development. Security updates are applied to the `main` branch only.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

Once versioned releases begin, this table will be updated to reflect which released versions receive security patches.

## Reporting a Vulnerability

If you discover a security vulnerability in Swasth AI, please **do not open a public GitHub issue**. Instead, report it privately so it can be addressed before public disclosure.

**To report a vulnerability:**
- Email: **your-email@example.com** *(replace with your actual contact email)*
- Alternatively, use GitHub's [private vulnerability reporting](https://github.com/arya-das111/SWASTH-AI/security/advisories/new) feature (Security tab → "Report a vulnerability")

**Please include:**
- A description of the vulnerability and its potential impact
- Steps to reproduce the issue (if applicable)
- Any relevant logs, screenshots, or proof-of-concept code

**What to expect:**
- **Acknowledgment:** within 48–72 hours of your report
- **Initial assessment:** within 7 days, including whether the issue is confirmed
- **Resolution timeline:** communicated once the issue is triaged, depending on severity
- **Disclosure:** we ask that you allow time for a fix to be released before any public disclosure. Credit will be given to reporters (unless you prefer to remain anonymous)

## Scope

Given that Swasth AI handles healthcare-related data (patient footfall records, facility data, staff attendance, and ABDM/FHIR-linked identifiers), please pay special attention to and report:
- Authentication/authorization bypass
- SQL injection or ORM query manipulation
- Exposure of PII or health data (DPDP compliance issues)
- Insecure API endpoints or missing access controls
- Vulnerabilities in offline sync/queue mechanisms that could lead to data tampering

Thank you for helping keep Swasth AI and the health data it manages secure.
