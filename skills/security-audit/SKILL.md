---
name: security-audit
description: Audit source code for OWASP Top 10 vulnerabilities — injection, broken auth, sensitive data exposure, misconfiguration, and more — producing a severity-ranked finding list with file locations and specific remediations.
compatibility: Requires Read, Glob, Grep for local codebases. Performs static analysis only — cannot detect runtime or infrastructure vulnerabilities without source access.
allowed-tools: Read Glob Grep
metadata:
  author: fabianmagrini
  version: "1.0"
  last-updated: 2026-05-10
---

Audit the target code for exploitable security vulnerabilities grounded in what the code actually does.

This is the code-level counterpart to `/threat-model`. Use this skill to find vulnerabilities in existing code. Use `/threat-model` to model threats in an architecture before or during design.

## Determine the target

Accept any of:
- A directory: `src/api/`, `services/payments/`
- A file: `src/auth/session.ts`, `app/controllers/users_controller.rb`
- A concern: `authentication`, `input validation`, `secrets handling`
- No argument — audit the full repository (note scope limitations for large repos)

If the target is a single concern (e.g. "authentication"), focus discovery on the relevant code paths rather than the full codebase. State what was and was not examined.

## Discovery steps

Work through each area systematically. For each finding, record: OWASP category, file and line reference, the vulnerable pattern, and a concrete remediation. Do not report a finding without a specific file location or grep evidence.

### 1. Injection (OWASP A03)

**SQL injection** — Grep for raw string interpolation into queries:
- `"SELECT * FROM ... WHERE id = " + `, `f"SELECT ... {user_input}"`, `query.format(`, `sprintf("SELECT`
- Look for ORM raw query escape hatches: `.raw(`, `execute(`, `query(`, `db.Exec(`
- Parameterized queries and ORM methods (`where(id: id)`, `filter(id=id)`) are safe — do not flag these

**Command injection** — Grep for shell execution with user-controlled input:
- `exec(`, `spawn(`, `subprocess.run(`, `os.system(`, `child_process`, `Runtime.exec(`
- Flag when the argument includes a variable, string concatenation, or template literal containing input

**Template injection** — Grep for server-side template rendering with unescaped user input:
- `render_template_string(`, `Template(user_input)`, `env.from_string(`
- Check whether auto-escaping is enabled in template engine config

**Path traversal** — Grep for file operations that include user-controlled paths:
- `fs.readFile(req.params`, `open(request.args`, `path.join(`, `__dirname + req.query`
- Look for missing `path.resolve` + prefix validation

### 2. Broken Authentication (OWASP A07)

- Grep for session management: `session.secret`, `cookie.secret`, `JWT_SECRET`, `SECRET_KEY` — flag hardcoded values or values read directly without validation that they are set
- Grep for password hashing: look for `bcrypt`, `argon2`, `scrypt`, `PBKDF2` — flag plain MD5/SHA1/SHA256 used for passwords, or passwords stored in plaintext
- Grep for token validation: look for `jwt.verify(`, `verify_token(` — flag missing signature verification (`jwt.decode(` without verify, `algorithms=["none"]`)
- Check session expiry: grep for `maxAge`, `expires`, `session_timeout` — flag missing or overly long session lifetimes
- Grep for rate limiting on auth endpoints: `rateLimit(`, `throttle(`, `@RateLimit` on `/login`, `/token`, `/password` routes — flag absence

### 3. Sensitive Data Exposure (OWASP A02)

**Hardcoded secrets** — Grep for:
- Patterns: `password = "`, `api_key = "`, `secret = "`, `AWS_SECRET`, `PRIVATE_KEY` directly assigned to string literals
- Look inside config files, test fixtures, and migration files — not just application code
- Note: environment variable reads (`process.env.SECRET`) are not hardcoded; flag missing validation that they are non-empty

**Sensitive data in logs** — Grep for logging calls near sensitive fields:
- `console.log(password`, `logger.info(token`, `print(credit_card`, `log.Printf(password`
- Check error handlers — stack traces containing request bodies can leak sensitive fields

**Sensitive data in responses** — Read model serializers and API response builders. Check whether password hashes, internal IDs, secrets, or PII fields are excluded from responses.

**Unencrypted storage** — Grep for database field definitions containing `password`, `ssn`, `credit_card`, `token` — check whether they use encrypted column types or application-level encryption.

### 4. Broken Access Control (OWASP A01)

**Missing authorization checks** — For each route handler, check whether a user-ownership check is performed before returning or modifying a resource:
- `findById(req.params.id)` without `where: { userId: req.user.id }` is a potential IDOR
- Grep for admin-only operations: `DELETE /users`, `GET /admin` — verify role checks are present

**Mass assignment** — Grep for patterns that bind request body directly to a model:
- `User.create(params)`, `Object.assign(user, req.body)`, `user.update_attributes(params)`
- Check whether a permitted attributes list (`permit(`, `@Validated`, `class-transformer`) is applied

**Forced browsing** — Check whether static files, admin routes, or internal APIs are protected or accessible without auth.

### 5. Security Misconfiguration (OWASP A05)

- Read CORS configuration: `cors({ origin: "*" })`, `Access-Control-Allow-Origin: *` — flag wildcard origins on authenticated APIs
- Read HTTP security headers config: check for `helmet(`, `Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security` — flag absence on web-facing services
- Grep for debug mode in production config: `DEBUG = True`, `NODE_ENV !== "production"` checks, `app.use(errorHandler())` in production
- Read cookie settings: `httpOnly`, `secure`, `sameSite` — flag missing `secure` or `httpOnly` on auth cookies
- Grep for default credentials: `admin/admin`, `root/root` in config or seed files

### 6. Insecure Deserialization (OWASP A08)

- Grep for deserialization of user-controlled data: `pickle.loads(`, `yaml.load(` without `Loader=yaml.SafeLoader`, `Marshal.load(`, `ObjectInputStream`, `JSON.parse(` applied to raw user input without schema validation
- Check whether deserialized objects are used in security-sensitive operations (eval, exec, privilege checks)

### 7. Cryptography failures (OWASP A02)

- Grep for weak algorithms: `MD5`, `SHA1` used for integrity or password hashing (not HMAC signature verification where MD5 may be acceptable)
- Grep for random number generation: `Math.random()`, `rand()` used for tokens, session IDs, or CSRF values — flag non-cryptographic RNG
- Grep for TLS configuration: `rejectUnauthorized: false`, `verify=False`, `ssl._create_unverified_context` — flag disabled certificate verification
- Check key sizes where visible: RSA < 2048 bits, EC curves weaker than P-256

### 8. Server-Side Request Forgery (OWASP A10)

- Grep for HTTP client calls that include user-controlled URLs: `fetch(req.body.url`, `requests.get(user_url`, `axios.get(params.url`
- Check whether an allowlist of permitted hosts is validated before the request is made
- Flag internal IP ranges in allowlists or missing host validation entirely

### 9. Logging and monitoring gaps (OWASP A09)

- Grep for auth event logging: failed login attempts, token rejections, permission denials — flag absence
- Check error handlers: unhandled exceptions that return generic 500 without logging are a monitoring gap
- Flag if no structured logging library is in use (`console.log` only in Node.js, `print` only in Python)

## Output format

Respond inline — do NOT write a file unless the user passes `--save`.

### Security Audit: `{target}`

**Scope**

What was examined and what was not (files read, concerns covered, known limitations of static analysis).

**Summary**

| Severity | Count |
|----------|-------|
| Critical | {n} |
| High | {n} |
| Medium | {n} |
| Low | {n} |
| Informational | {n} |

**Findings**

One entry per finding, ordered by severity descending:

> **[CRITICAL/HIGH/MEDIUM/LOW/INFO] OWASP {A0N}: {Category} — {Short title}**
> **Location:** `{file}:{line}` (or grep pattern)
> **Evidence:** The specific code pattern that is vulnerable.
> **Impact:** What an attacker can achieve by exploiting this.
> **Remediation:** Specific fix — library, function, or pattern to use instead.

**What looks good**

Bullet list of security controls that are correctly implemented — only include controls that are genuinely present and effective. Do not pad this section.

**Recommended next steps**

Ordered by risk reduction value:
1. {Highest-priority remediation — specific file and change}

## Gotchas

- Do not report a finding without a specific file location or code evidence. "The app might have SQL injection" is not a finding. "Unsanitized user input concatenated into a query at `src/db/users.ts:42`" is a finding.
- Framework-provided protections are real mitigations. Django ORM parameterizes queries by default; Rails strong parameters prevent mass assignment by default. Credit these and do not report them as vulnerabilities.
- A missing security header is a LOW or MEDIUM finding — not Critical. Reserve Critical for findings that are directly exploitable with no prerequisites.
- Static analysis cannot find all vulnerabilities. Authentication logic timing attacks, race conditions, and business logic flaws require runtime analysis. State this limitation at the top of the report.
- Hardcoded secrets in test files are still findings — test databases and API keys are frequently reused, and test files often get committed to public repositories accidentally.
- Do not conflate "could be a vulnerability" with "is a vulnerability." A `path.join` with user input is only a path traversal if there is no prefix validation. Read the surrounding code before reporting.
- This skill pairs naturally with `/threat-model` (architectural threat analysis to complement code-level findings), `/dependency-risk` (vulnerable third-party packages are OWASP A06 and warrant a separate analysis), and `/review-code` (a security audit finding in a specific file warrants a full code review of that file).
