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

## [October 2026] - Swagger 2.0 Support

### Added
- Swagger 2.0 support (translates \#/definitions/\, \#/parameters/\, and \#/responses/\ refs)
- Tested against Kubernetes API (Swagger 2.0, 4.4 MB, 1,000+ endpoints). Validation errors: 0. Raw \ leaks: 0.

## [October 2026] - Response Schema Rendering

### Added
- Response schemas are now rendered as Markdown tables in the generated documentation.
- Handles both OpenAPI 3.x (content -> schema) and Swagger 2.0 (schema directly).
- Resolves $ref in response objects and schemas.
