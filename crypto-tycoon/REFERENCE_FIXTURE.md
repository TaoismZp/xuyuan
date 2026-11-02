# Crypto Tycoon — Reference Fixture v2

## Canonical Effect Image
The approved 16:9 concept image from the 2026-11-02 session is the **effect drawing / Vision Fixture** for the rebuild.

- canonical dimensions: **1672 × 941**
- locked SHA-256: `5b0c5d5d4f8f9afbd2af5e8dddbd77e749975006873262efadd02125ac68a039`
- visual intent: polished commercial casual-game screenshot, not a webpage/dashboard
- role: **judge only; never runtime scenery**

The existing `keyart-chunk-*.js` files are deprecated evidence copies from the failed v3 experiment. They may be used only for visual comparison tooling. They are forbidden from the production runtime and must not be imported by the accepted rebuild.

## Must-match qualities
1. **World, not tilted UI** — a volumetric board with real spatial depth and authored landmarks.
2. **Hero board silhouette** — a square-loop tycoon board dominates the frame with a luminous central market/title stage.
3. **Authored tile landmarks** — exchange tower, bull, bear, rocket/halving, whale, mining rig, staking/vault, NFT/DeFi motifs.
4. **Character tokens** — four differentiated stylized player pieces, not colored dots, emoji or generic primitive stacks.
5. **Material hierarchy** — gold, glass/neon, dark metal, colored enamel tiles, reflections/highlights and contact shadows.
6. **Lighting** — warm gold key light + cyan/violet finance-neon rim lighting; visible depth and separation.
7. **Integrated game HUD** — leaderboard, round/goal, compact actions and a large dice control arranged around the board, not a generic side dashboard.
8. **Density** — central dice/coins/market stage plus skyline/backdrop detail; no large empty prototype zones.
9. **Game readability** — despite density, tile categories, player position, current action and market state remain legible.
10. **Mobile/iPad delivery** — the same game world survives tablet/mobile composition; it must not collapse into a different dashboard product.

## Allowed divergence
- exact crypto logos, character faces, tile wording and building shapes may differ;
- geometry may simplify for mobile performance;
- gameplay content may exceed the effect image;
- camera may shift slightly on iPad to preserve board readability.

## Forbidden shortcuts
Under `WISH_DELIVERY_V7.md` v7.5 Reference Non-Substitution Rule, the accepted build may NOT:
- use the effect image or its reduced copy as a background/backplate;
- use screenshots of the old game as UI or scenery;
- use 2D renders to impersonate real-time hero geometry;
- hide missing geometry behind blur, darkness, bloom, fog or HUD panels;
- count semantic presence ("there is a bull") as perceptual match.

## Comparative Quality Gate
Before Final, capture the **actual active-play state** on the real public surface at desktop 1672×941 and iPad landscape. Compare desktop beside the locked effect image at equal displayed size and score:
- silhouette / composition
- depth / volume
- authored forms
- materials
- lighting
- character quality
- landmark density
- UI-world cohesion
- readability
- desirability

Automatic FAIL if:
- the pair reads as “concept art vs ordinary webpage / dev scene”;
- a hero asset still reads first as box/sphere/cone assembly;
- the game depends on the Reference Fixture pixels to look finished;
- active play looks materially worse than intro/key art.
