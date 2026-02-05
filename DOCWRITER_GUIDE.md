# Docwriter Agent: Adaptability Guidelines

## Core Principle: Read .gitignore First

Before documenting ANY project, read `.gitignore` and ask:

**"What's intentionally NOT in this repository?"**

Your answer determines the entire documentation strategy.

---

## Pattern Recognition

### Pattern 1: Production Code Gitignored (Internal Tools)

**Indicator in .gitignore:**
```
# Production scripts with credentials (never push to GitHub)
/production_script.py
/deploy_script.sh
/real_config.yaml
```

**What this means:**
- ❌ Real production code is NOT in the repo
- ✅ Templates/examples ARE in the repo (usually in `docs/` or `templates/`)
- ✅ Documentation teaches "copy template, customize"
- 🔐 Secrets are never pushed anywhere

**Docwriter strategy:**
1. **Document the templates**, not the missing scripts
2. **Verify templates exist** in docs/ (not scripts in root)
3. **Example paths don't match actual deployment** (that's normal!)
4. **Focus on: "Here's how to adapt the template to your setup"**
5. **Never expect to verify production paths** (they're intentionally absent)

**Example: HannaWebScraper**
- Real scripts (`scrape_to_n8n.py`) are gitignored
- Look in `docs/scrapers/` for templates
- Document how to copy and customize
- Don't verify paths in root (they won't be there)

### Pattern 2: Production Code NOT Gitignored (OSS/Public)

**Indicator in .gitignore:**
```
.env
__pycache__/
*.pyc
# NO mention of "don't push scripts"
```

**What this means:**
- ✅ Real production code IS in the repo
- ✅ Only credentials are gitignored (`.env`, `.key`, etc.)
- ✅ Users clone and use directly
- 🌍 Designed for public consumption

**Docwriter strategy:**
1. **Verify all code paths exist** in the repo
2. **Verify examples match actual code** (they should be identical)
3. **Paths in docs should be exact** and verifiable
4. **Focus on: "Clone and deploy"** not "customize template"
5. **Check that documentation examples work as-is**

**Example: MansionRadio**
- Source code (`bot.py`, `main.py`) is committed
- Can verify all paths actually exist
- Examples should work exactly as documented
- Document as "clone and run"

---

## Verification Checklist by Pattern

### For Internal Tool Projects (Pattern 1)

- ✅ Template files exist in `docs/` or designated template folder
- ✅ Template naming is consistent (`*.example`, `*.template`, `_template_*`)
- ✅ Documentation explains how to customize each template section
- ✅ Examples use placeholder values (not real production values)
- ⚠️ DON'T expect root-level production scripts to exist
- ⚠️ DON'T verify paths that are intentionally gitignored
- ✅ Verify .gitignore comments explain the intent clearly
- ✅ Check that templates have enough guidance for users to customize

### For OSS/Public Projects (Pattern 2)

- ✅ All referenced files actually exist in the repo
- ✅ Examples exactly match production code
- ✅ Example configs (`.example` files) match real configs perfectly
- ✅ Documentation paths are verifiable against repo structure
- ✅ Code can be tested directly from examples
- ✅ No credentials should appear in ANY committed file
- ✅ Examples should work as-is after cloning

---

## How to Detect the Pattern

### Check These Files (In Order)

1. **`.gitignore`** - MOST IMPORTANT
   - Look for "never push" or "production" comments
   - Look for `/production_*` or `/real_*` patterns
   - Look for what's explicitly excluded

2. **`README.md`** - Understand deployment model
   - "Copy template and customize" → Pattern 1 (Internal)
   - "Clone and configure" → Pattern 2 (OSS)

3. **`docs/` folder structure**
   - Has `examples/`, `templates/`, `scrapers/` subdirs → Pattern 1
   - Has deployment guides, architecture docs → Pattern 2

4. **Root folder contents**
   - Lots of `.example` files, no real configs → Pattern 1
   - Real configs committed (`.env` gitignored) → Pattern 2

5. **License file**
   - MIT, Apache, GPL → Pattern 2 (OSS intended)
   - No public license → Pattern 1 (Internal use)

### Quick Decision Tree

```
Does .gitignore say "never push to GitHub"?
├─ YES → Pattern 1 (Internal Tool)
│  └─ Document templates in docs/
│
└─ NO → Does .gitignore ignore .env and generated files only?
   ├─ YES → Pattern 2 (Public OSS)
   │  └─ Verify paths in docs match repo structure
   │
   └─ UNCLEAR → Read README carefully
      └─ Look for "clone" vs "customize" language
```

---

## Docwriter Adaptations Required

### For Pattern 1 Projects (HannaWebScraper Model)

**What docwriter must understand:**
- Templates might be in `docs/scrapers/` not root
- Real files won't be in the repo (expected!)
- Verify `.example` files match their documentation
- Don't verify paths that are intentionally absent
- Focus on: "Is the template clear and complete?"

**Modified verification checklist:**
- [ ] All templates in docs/ are documented
- [ ] Template examples show what values to replace
- [ ] Placeholder names are clear (`YOUR_API_KEY` vs `your_api_key`)
- [ ] `.gitignore` clearly explains what's excluded and why
- [ ] Documentation guides users through customization steps
- [ ] No credentials appear in ANY example files

**Example docwriter interaction:**
```
User: "Document the scraper setup"
Docwriter (checks .gitignore): "Ah, I see scrape_to_n8n.py is gitignored. 
Let me look in docs/scrapers/ for the template instead."
```

### For Pattern 2 Projects (MansionRadio Model)

**What docwriter must understand:**
- All code is committed and verifiable
- Examples should work exactly as-is
- Paths in docs must exist in repo
- Can verify all paths and links
- Focus on: "Does this example work?"

**Modified verification checklist:**
- [ ] All file paths in docs exist in repo
- [ ] Code examples match actual production code
- [ ] `.example` files are identical to their real counterparts (minus secrets)
- [ ] All internal links (docs → docs) work
- [ ] Examples can be tested directly from the repo
- [ ] No credentials in any committed file

**Example docwriter interaction:**
```
User: "Document deployment steps"
Docwriter (checks .gitignore): "I see main.py and bot.py are NOT ignored. 
Let me verify all paths in the docs actually exist."
[Verifies bot.py:line_number references are correct]
```

---

## Configuration for Docwriter

Projects should provide in `AGENTS.md` or similar:

```markdown
## Documentation Type

**Project Intent:** [ ] Internal Tool [ ] Public OSS

### If Internal Tool:
- Templates location: `docs/scrapers/` or `templates/`
- Template naming pattern: `*.example` or `_template_*`
- Users customize: Yes
- Deployment model: Copy template, customize locally
- Focus doc verification on: Template clarity and completeness

### If Public OSS:
- Source code committed: Yes
- Example configs: `*.example` files
- Users customize: Minimally (env vars)
- Deployment model: Clone and run
- Focus doc verification on: Path existence and accuracy
```

---

## Summary: The Key Insight for Docwriter

**`.gitignore` isn't just about what to exclude from version control.**

**It's a design specification that tells you:**

- What the project creator considers "production-only"
- What they consider "safe to share"
- How users are expected to deploy and customize
- Where templates and examples should go
- How seriously they take security

**Read .gitignore. Understand the intent. Adapt your verification strategy accordingly.**

That's what makes docwriter truly general-purpose.

---

**Last Updated:** 2026-02-05
