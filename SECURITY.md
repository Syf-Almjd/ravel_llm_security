# Security Policy

## Supported Versions

Ravel actively maintains and provides security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The Ravel core team takes the security of AI workflows and LLM agent gateways extremely seriously. If you discover a potential vulnerability in Ravel's pipeline, models, or backend services, please report it privately rather than opening a public issue.

### How to Report

1. **GitHub Private Vulnerability Reporting**:
   - Navigate to the **Security** tab of the [ravel_llm_security repository](https://github.com/Syf-Almjd/ravel_llm_security).
   - Click on **Report a vulnerability** to open a confidential advisory.
2. **Email**:
   - Alternatively, submit details to `security@ravel.dev` with the subject tag `[VULNERABILITY REPORT]`.

### Please Include:
- A descriptive summary of the issue (e.g. prompt injection bypass, auth token leakage, or unauthenticated route access).
- Steps to reproduce the vulnerability, including minimal example code or curl commands.
- Expected vs. actual behavior.
- Affected components (e.g. `Sanitizer`, `Guard-SLM`, `EASE Router`, `SessionModel`).
- Any proposed remediation or patch if available.

### Disclosure Policy

- We will acknowledge receipt of your report within **48 hours**.
- We will provide an assessment and targeted timeline for remediation within **5 business days**.
- Once a fix is verified, a patched release and security advisory will be published simultaneously, crediting the researcher (unless anonymity is requested).
