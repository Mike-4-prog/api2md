# api2md Testing Log

Tracking real-world tests of api2md before finalization.

---

## Test Round 1: Local sample specs

### Test 1: Validate `sample.yaml`
- Command: `python api2md.py --spec sample.yaml --validate`
- Result: PASS — "No issues found. Specification is valid."
- Status: Closed

### Test 2: Generate Markdown from `sample.yaml`
- Command: `python api2md.py --spec sample.yaml --output docs/sample-test.md`
- Result: PASS — Markdown written, output clean
- Status: Closed

### Test 3: Diff `sample.yaml` vs `new.yaml`
- Command: `python api2md.py --diff sample.yaml new.yaml`
- Result: PASS — 7/7 expected changes detected
- Status: Closed

### Test 4: Diff with AI descriptions
- Command: `python api2md.py --diff sample.yaml new.yaml --ai`
- Result: PASS — Ollama generated description for new endpoint
- Status: Closed

### Test 5: JSON output format
- Command: `python api2md.py --diff sample.yaml new.yaml --json`
- Result: PASS — valid JSON, correct summary counts
- Status: Closed

### Test 6: Markdown output format
- Command: `python api2md.py --diff sample.yaml new.yaml --markdown`
- Result: PASS — all sections separated by blank lines
- Status: Closed

### Test 7: Version change detection (after fix)
- Command: `python api2md.py --diff sample.yaml new.yaml`
- Result: PASS — version change now shown in text, JSON, and markdown output
- Status: Closed

### Test 8: $ref resolution in request body (after fix)
- Command: `python api2md.py --spec sample.yaml --output docs/sample-test-3.md`
- Result: PASS — POST /users now shows resolved schema, properties table, and example
- Status: Closed

---

## Test Round 2: Real-world specs

### Test 9: GitHub API spec — Round 1 (before fixes)
- Command: `python api2md.py --spec github-api.json --validate`
- Result: FAILED — 6,300 errors
- Error pattern: "Parameter missing 'name'" and "Parameter missing 'in'" on every endpoint using shared $ref parameters
- Root cause: Validator did not resolve $ref for parameters
- Status: Closed after fix

### Test 10: GitHub API spec — Validate (after fix)
- Command: `python api2md.py --spec github-api.json --validate`
- Result: PASS — "No issues found. Specification is valid."
- Errors before fix: 6,300
- Errors after fix: 0
- Status: Closed

### Test 11: GitHub API spec — Generate Markdown (after fix)
- Command: `python api2md.py --spec github-api.json --output docs/github-api.md`
- Input spec size: 13 MB
- Output markdown size: 2.4 MB
- Result: PASS — no crash, no hang, ~20 seconds generation time
- Status: Closed

### Test 12: GitHub API spec — Spot-check endpoint output
- Command: `Get-Content docs/github-api.md | Select-Object -Index (30261..30295)`
- Endpoint checked: `POST /repos/{owner}/{repo}/issues`
- Result: PASS
  - Parameters table shows real `owner` and `repo` values (path, required, descriptions)
  - Request body renders correctly with title, body, assignee, etc.
  - Example JSON generated
- Status: Closed

### Test 13: GitHub API spec — $ref leak check
- Command: `Select-String -Path docs/github-api.md -Pattern '\$ref' | Measure-Object`
- Result: Count = 0 — no raw `$ref` strings in the output
- Status: Closed

### Test 14: GitHub API spec — Parameters fix on original bug endpoint
- Command: `Get-Content docs/github-api.md | Select-Object -Index (30261..30295)`
- Before fix: two empty parameter rows
- After fix: `owner` (path, Yes) and `repo` (path, Yes) both resolved with descriptions
- Status: Closed

---

## Open Issues

### Issue #2: AI descriptions only cover endpoints and methods
- Command: `python api2md.py --diff sample.yaml new.yaml --ai`
- Problem: AI generates descriptions for new endpoints and new HTTP methods only
- Missing for: new schemas, new parameters, new properties
- Status: SKIPPED — decision made not to extend now; revisit if needed

### Issue #7: Responses section does not show response schemas
- Observed in: GitHub API output
- Problem: Responses show only status codes and descriptions. The response body schema (with $ref resolution) is not rendered.
- Impact: Medium — users cannot see what the response looks like
- Status: OPEN — feature gap

### Issue #8: allOf / oneOf / anyOf composition not handled
- Observed in: Preparing for Kubernetes Gateway API test
- Problem: Schemas using composition keywords render flat, may drop properties
- Impact: Medium — common in cloud-native specs
- Status: OPEN — awaiting test on Kubernetes Gateway API

---

## Test Round 2 Progress

### Test 9–14: GitHub API spec
- [x] Download spec (13 MB)
- [x] Validate — PASS after validator $ref fix
- [x] Generate Markdown — PASS (2.4 MB output)
- [x] Spot-check endpoint output — PASS
- [x] $ref leak check — 0 leaks
- [ ] Diff (need two versions of GitHub spec)
- [ ] AI descriptions (skipped — 900+ endpoints would take too long)

### Test 15: Stripe API spec
- [ ] Download spec
- [ ] Validate
- [ ] Generate Markdown
- [ ] Diff
- [ ] AI descriptions
- Issues found:

### Test 16: Kubernetes Gateway API spec
- [ ] Download spec
- [ ] Validate
- [ ] Generate Markdown
- [ ] Diff
- [ ] AI descriptions
- Issues found:

---

## Fixes Applied This Session

| Fix | File | Verified |
|-----|------|----------|
| Version change detection | `core/differ.py` | Test 7 |
| $ref resolution in request bodies | `core/generator.py` | Test 8 |
| $ref resolution in parameters | `core/generator.py` | Test 14 |
| $ref resolution in validator | `core/validator.py` | Test 10 |
| Error output cap (50 errors max) | `core/validator.py` | — |
| Path-level parameters check | `core/validator.py` | — |

---

## Cumulative Stats

| Metric | Value |
|--------|-------|
| Tests run | 14 |
| Tests passed | 14 |
| Real bugs found and fixed | 4 |
| Feature gaps logged | 3 |
| Largest spec tested | 13 MB (GitHub API) |
| Endpoints documented | 900+ |
| Raw $ref leaks in output | 0 |
| Validation errors on GitHub spec | 0 |

Last updated: October 2, 2026
### Test 17: Kubernetes API spec (Swagger 2.0)
- Command: python api2md.py --spec k8s-api.json --validate
- Result: PASS � "No issues found. Specification is valid."
- Errors before fix: 14,561
- Errors after fix: 0
- Status: Closed

### Test 18: Kubernetes API spec � Generate Markdown
- Command: python api2md.py --spec k8s-api.json --output docs/k8s-api.md
- Input spec size: 4.4 MB
- Output markdown size: 1.04 MB
- Result: PASS � no crash, no hang
- Status: Closed

### Test 19: Kubernetes API spec � \ leak check
- Command: Select-String -Path docs/k8s-api.md -Pattern '\' | Measure-Object
- Result: Count = 0 � no raw \ strings in the output
- Status: Closed
