# Capability selection record — CHAIN TYCOON v1

## Selected methods

1. **OpenAI web-game-foundations**
   - Serializable simulation state separated from rendering/HUD.
   - Explicit turn loop, input boundary, and save state.

2. **OpenAI develop-web-game**
   - Deterministic `?test=1` RNG.
   - `window.render_game_to_text` and `window.advanceTime` hooks.
   - Real browser end-to-end regression on localhost and public delivery surface.

3. **Agentic game-design-space method**
   - Rejected a literal property-renaming clone.
   - Added market regimes, sector completion, forced liquidation, heterogeneous bots, and crypto-native dilemma events.

## Rejected directions

- Pure Monopoly reskin: too cosmetic.
- Pure portfolio simulator: not enough board-game tension.
- Live token prices / wallet connection: unnecessary dependency for a self-contained game.

## Product contract

Playable in a mobile browser with no login, wallet, install, or API key.
