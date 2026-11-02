# Crypto Tycoon — Asset Manifest v1

## Production Strategy
The visual bottleneck is commercial 3D art fidelity, not game logic. Use a hybrid pipeline:
1. Locked key-art reference for composition and perceptual target.
2. Authored Three.js geometry for interactive hero objects, tokens, dice, landmarks, lights and VFX.
3. Reference-derived 2.5D environment/backplate where full real-time reconstruction adds little interaction value but strongly improves perceptual match.
4. Replace temporary procedural stand-ins only when they are visible in the reference camera and fail the silhouette/material bar.

## Hero Assets — must pass first
| Asset | Role | Required look | Source |
|---|---|---|---|
| Central logo + crown | Main focal point | thick gold 3D lettering / plaque, warm rim, layered depth | Three.js text/sprite + extruded plaque |
| Market globe / ticker stage | Center motion | cyan holographic globe + candlestick ring + gold pedestal | Three.js geometry + canvas textures |
| Dice pair | Primary action prop | ivory/gold rounded dice, physical roll animation, contact shadow | Three.js rounded box approximation |
| Human astronaut token | Player hero | collectible toy silhouette with helmet, backpack, gold base | procedural authored model |
| Doge token | Bot hero | sunglasses dog collectible, chain/coin cue, red/gold base | procedural authored model |
| NFT pixel token | Bot hero | pixel-head collectible, blue neon base | procedural authored model |
| Bull token | Bot hero | bull collectible with horns/sunglasses, green base | procedural authored model |

## Signature Landmarks — at least 6 visible
- Exchange tower with roof logo and market screen.
- Bull-market sculpture with rising arrow.
- Bear-market sculpture with falling arrow.
- Halving rocket with plume/cloud base.
- Whale with neon BTC badge.
- NFT display / pixel portrait.
- Mining rig cluster.
- Staking vault / lock stack.
- Airdrop parachute package.
- Liquidation warning / broken platform.

## Environment Kit
- Neon crypto city skyline with 3 depth layers.
- Financial chart billboard.
- Floating BTC / ETH holograms.
- Coin/chip stacks around board.
- Event-card and market-card decks in foreground.
- Edge rail lights and gold trim.
- Small practical lamps / signs to remove dead zones.

## UI Assets
- 4 ranked player cards with portrait circles.
- Round / objective panel.
- Vertical utility buttons.
- Oversized circular physical roll control.
- Asset / event modal using same gold/navy toy-casino language.

## VFX
- Dice roll: squash/ease + gold spark burst.
- Movement: base glow pulse + short light trail.
- Buy asset: coin burst + tile rim pulse.
- Bull / bear: green or red board-wide sweep.
- Airdrop: descending package + confetti.
- Liquidation: red shock ring + camera micro-shake.
- Halving: rocket plume + gold radial pulse.

## Rejection Rules
Reject any asset if one of these is true in the main active camera:
- reads as sphere/box/cone assembly before reading as the intended object;
- needs a text label to explain what it is;
- flat color/emissive replaces material authorship;
- no contact with the world (floating/no shadow/no base);
- detail disappears at thumbnail size because silhouette is generic;
- occupies reference hero space but has no comparable visual weight.

## Vertical Slice Scope
Before full production, only the following need to be finished to target quality:
- central stage;
- 8–10 front/right/upper visible tiles;
- astronaut + Doge + NFT + bull tokens;
- exchange, bull, whale, rocket, NFT, staking landmarks;
- foreground dice + coin stacks;
- skyline + chart screen;
- real HUD.

If that active-play screenshot still feels like a different product class from the locked reference, do not expand the remaining board.
