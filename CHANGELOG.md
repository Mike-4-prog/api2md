# Changelog

All notable changes and validations for api2md are documented here.

## [Unreleased] - October 2026

### Added & Validated
- Tested against GitHub API (13 MB, 900+ endpoints). Validation errors: 0. Raw $ref leaks in output: 0.
- Tested against Stripe API (8.3 MB). Validation errors: 0. Raw $ref leaks in output: 0.
- Added $ref resolution for parameters, request bodies, and validator checks.
- Added version change detection across text, JSON, and Markdown outputs.
- Added composition handling (llOf, nyOf, oneOf).

### Known Issues
- Kubernetes Gateway API test blocked by lack of Swagger 2.0 support (in progress).
- Response schemas are not yet rendered in Markdown output.
