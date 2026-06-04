# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Reporting a Vulnerability

We take the security of the LPU AI Academic Advisor seriously. If you believe you have found a security vulnerability, please report it professionally.

1. **Do not** open a public issue.
2. Send a detailed report to the maintainers (e.g., via GitHub private message or designated contact).
3. Include as much information as possible:
   - Type of issue (e.g., credential exposure, SQL injection).
   - Steps to reproduce.
   - Potential impact.

We will acknowledge your report and provide a timeline for a fix.

## Credential Safety
- Never commit your `.env` file.
- Use the provided `.env.example` as a template.
- Rotate your `PUTER_TOKEN` and `DATABASE_URL` credentials periodically.
