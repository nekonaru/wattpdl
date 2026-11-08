# Security Policy

## Reporting a Vulnerability

If you find a security issue in wattpdl, please report it privately through GitHub:

1. Go to the [Security tab](https://github.com/nekonaru/wattpdl/security) of this repository
2. Click **Report a vulnerability**
3. Describe the issue, the impact, and the steps to reproduce it

Please do not open a public issue for security problems. You can expect an acknowledgement within a few days.

Only the latest released version is supported with security fixes.

## Scope Notes

wattpdl only talks to public endpoints on wattpad.com and PyPI. It does not handle credentials, and it stores its state in `~/.wattpdl/` on your machine. Reports about Wattpad itself should go to Wattpad.
