# Crypto Tycoon — Asset Manifest v2

## Production Strategy
The production bottleneck is **commercial 3D art fidelity**, not rules, deployment or CI.

The rebuild uses a true real-time 3D pipeline. The previous `reference-derived 2.5D environment/backplate` strategy is revoked.

Priority order follows `threejs-aaa-graphics-builder`:

**authored forms → materials → lighting → effects**

Reference pixels are not allowed in the runtime.

## Hero Assets — Vertical Slice must prove these first
| Asset | Role | Required look | Production source | Reject if |
|---|---|---|---|---|
| Central title/crown monument | Main focal point | layered gold monument, crown, crypto medallion, physical depth | authored Three.js geometry + vector/canvas text texture only for lettering | looks like flat UI plaque |
| Market globe/ticker stage | Center motion | glass cyan globe, candlestick halo, pedestal, emissive rings | authored Three.js geometry + shader/canvas data texture | just a glowing sphere |
| Dice pair | Primary action prop | bevelled ivory/gold dice, recessed pips, physical roll | authored rounded geometry | raw cubes |
| Astronaut token | Player hero | collectible toy astronaut, helmet/visor/backpack/base | authored multi-part 3D model; generated/imported GLB preferred if capability available | reads as capsules/spheres |
| Doge token | Bot hero | stylized dog collectible, glasses/chain/base | authored multi-part model or imported/generated GLB | needs label to read as dog |
| NFT token | Bot hero | pixel/cyber collectible, strong head silhouette | authored model or imported/generated GLB | generic box person |
| Bull token | Bot hero | muscular toy bull, horns, glasses/base | authored model or imported/generated GLB | sphere + cone horns |

## Signature Landmarks — minimum 8 authored hero props
1. Exchange tower with layered roof crown and live market facade.
2. Bull-market sculpture with upward chart motif.
3. Bear-market sculpture with downward chart motif.
4. Halving rocket with engine/plume gantry.
5. Whale sculpture with BTC medallion and water/light base.
6. Mining rig cluster with fans/frames/cables/light strips.
7. Staking vault with lock, coin stack and yield hologram.
8. NFT gallery / pixel portrait kiosk.
9. Airdrop parachute crate.
10. Liquidation hazard platform / warning beacon.

At least 6 must be visible in the reference camera; at least 8 must exist before full-board expansion.

## Board Kit
- thick square-loop board base with rounded corners and layered trim;
- 24 raised tile plinths with chamfer/bevel profile;
- gold edge rail + cyan under-lighting;
- per-tile category icon plate;
- ownership ring / level pylons;
- physical corner structures, not blank corners;
- central recessed stage with 2–3 elevation levels.

## Environment Kit
- three depth layers of authored skyline silhouettes;
- rooftop antennas / billboards / chart panels;
- coin/chip clusters in foreground and board edges;
- holographic BTC / ETH / chart elements;
- small practical lamps, rails, cables, vents and signs;
- distant haze only after geometry exists.

## Material Library
- polished gold metal;
- dark blue-black lacquer;
- glossy enamel tile colors;
- ivory resin/plastic;
- tinted glass/cyan hologram;
- matte toy resin;
- dark brushed metal;
- emissive cyan/magenta/red/green accents.

Each material needs visible roughness/metalness separation. Emissive must never be the only detail source.

## Lighting Rig
- warm key from upper-left/front;
- cyan rim from right/back;
- violet ambient fill;
- soft contact shadows under all hero assets;
- practical emissive lights in environment;
- tone mapping and bloom only after material/geometry review.

## UI Assets
- compact 4-player leaderboard with portrait medallions;
- round / objective plaque;
- three contextual action chips;
- oversized physical roll control visually anchored near the board;
- modal cards with gold/navy toy-casino language;
- tablet layout preserving the same 3D world.

## VFX
- dice roll sparks + contact bounce;
- player move trail + landing pulse;
- buy asset coin burst + ownership ring;
- bull/bear green/red sweep;
- airdrop descent + confetti;
- liquidation shock ring + camera micro-shake;
- halving rocket plume + gold radial pulse.

VFX is polish, not geometry replacement.

## Performance Budget (iPad Safari target)
Vertical slice target before optimization:
- draw calls: target < 180, hard ceiling 260;
- visible triangles: target < 350k, hard ceiling 600k;
- texture memory: avoid large unique textures; prefer atlases/canvas textures;
- pixel ratio capped around 1.5–1.75 on tablet;
- shadows only for hero lights / critical objects;
- repeated city/rail/coin props instanced.

## Vertical Slice Scope
Before full production, finish only:
- full board base + 10–12 visible high-quality tiles;
- central title/crown + market globe stage;
- 4 player tokens;
- exchange, bull, bear, whale, rocket, staking landmarks;
- foreground dice + coin stacks;
- 3-layer skyline + one chart billboard;
- real HUD;
- final camera / materials / lighting / tone mapping.

If this active-play screenshot still feels like a different product class from the locked Reference Fixture, full board expansion is forbidden.
