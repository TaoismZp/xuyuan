# Existing GitHub Issue + Actions publisher — control

The repository already contains `.github/workflows/publish-longform.yml` for the earlier `longform-v2` spike.

Strengths:
- no new auth system: GitHub login is the owner identity
- no external CMS service, server, or database
- native Git history after generated files are committed
- owner-only guard already exists (`issue.user.login == TaoismZp` + title prefix)

Weaknesses against the personal-site backend contract:
- authoring happens in an Issue Form, not a dedicated longform editor
- preview/editing ergonomics are weak on mobile for very long text
- draft/published state is awkward; an open Issue is not a clean content lifecycle
- edit/unpublish semantics are workflow conventions rather than first-class CMS behavior
- article metadata/body parsing is coupled to the issue template

It remains the no-CMS baseline. It is useful as a fallback publishing transport, but it should not win merely because it is already present.
