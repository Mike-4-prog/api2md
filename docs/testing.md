# Testing and Validation

api2md was validated against large, real-world OpenAPI specifications to ensure it handles complex schemas without breaking.

## Tested Specs

| Spec | Size | Endpoints | Validation Errors | Raw $ref Leaks |
|------|------|-----------|-------------------|------------------|
| GitHub API | 13 MB | 900+ | 0 | 0 |
| Stripe API | 8.3 MB | 500+ | 0 | 0 |

## How Testing Was Done

1. Downloaded raw OpenAPI JSON files for GitHub and Stripe.
2. Ran python api2md.py --spec <file> --validate to ensure the specs passed validation after ref resolution.
3. Ran python api2md.py --spec <file> --output <file.md> to generate Markdown.
4. Ran string searches on the output for $ref to ensure no unresolved references leaked into the final documentation.
5. Spot-checked complex endpoints to ensure path parameters and request bodies resolved correctly.

For detailed test-by-test logs, see the [test-log.md](../test-log.md) file.
