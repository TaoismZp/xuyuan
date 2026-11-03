# Payload CMS representative assessment

Payload is a serious full CMS, not a lightweight Git editor for this project.

Representative mapping:
- owner auth: native Payload auth
- drafts/versions: native Payload versions and drafts
- rich text: native Lexical editor
- storage: database-backed, not the Git Markdown source used by the accepted frontend
- deployment: requires a Next.js/Payload runtime plus database; official one-click paths pair Vercel with Neon/Blob or Cloudflare with D1/R2
- integration cost: either add a separate CMS/API build pipeline or migrate the accepted frontend into the Payload/Next.js app

Hard-gate result for this project: Payload must prove a major authoring gain to justify adding a runtime/database and a second source-of-truth model. The current representative task does not need that complexity, so no production Payload scaffold is created during capability procurement.
