# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by emailing the maintainers directly rather than opening a public issue.

**Please do not report security vulnerabilities through public GitHub issues.**

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any suggested fixes or mitigations

## Security Considerations

### API Keys and Credentials

- Never commit API keys, passwords, or other credentials to the repository
- Use environment variables for sensitive configuration
- Rotate credentials regularly

### Data Handling

- All collected data is public Reddit content
- No personal or private information is collected
- Data is stored in accordance with platform terms of service

### Dependencies

- Dependencies are regularly updated to address security vulnerabilities
- Use `pip audit` to check for known vulnerabilities in dependencies

## Response Timeline

- We will acknowledge receipt of vulnerability reports within 48 hours
- We will provide an initial assessment within 5 business days
- We will work to address critical vulnerabilities within 30 days

## Disclosure Policy

- We follow responsible disclosure practices
- Security fixes will be released as soon as possible
- Credit will be given to security researchers who responsibly disclose vulnerabilities