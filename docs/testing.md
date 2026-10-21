# Testing and Validation

api2md was validated against large, real-world OpenAPI and Swagger specifications to ensure it handles complex schemas without breaking.

## Tested Specs

| Spec | Version | Size | Endpoints | Validation Errors | Raw \ Leaks |
|------|---------|------|-----------|-------------------|-----------------|
| GitHub API | OpenAPI 3.x | 13 MB | 900+ | 0 | 0 |
| Stripe API | OpenAPI 3.x | 8.3 MB | 500+ | 0 | 0 |
| Kubernetes API | Swagger 2.0 | 4.4 MB | 1,000+ | 0 | 0 |

## How Testing Was Done

1. Downloaded raw specification files for GitHub, Stripe, and Kubernetes.
2. Ran python api2md.py --spec <file> --validate to ensure the specs passed validation after ref resolution.
3. Ran python api2md.py --spec <file> --output <file.md> to generate Markdown.
4. Ran string searches on the output for \ to ensure no unresolved references leaked into the final documentation.
5. Spot-checked complex endpoints to ensure path parameters and request bodies resolved correctly.

For detailed test-by-test logs, see the [test-log.md](../test-log.md) file.
