# Render contract (AIOS.render event)

The load-bearing integration mechanism in the Jarvis-style LiveKit voice+HUD build: a backend Python voice agent and a frontend HUD dashboard join the same real-time room, and every tool call publishes JSON over the room's data channel under an `AIOS.render` event with 5 literal string types (brief, metrics, pipeline, intel, actions) that "must be byte-for-byte identical" between the Python publisher and the JS consumer. Documented in a generated `contract.md` but manually maintained — brittle by construction, with no schema validation shown.

## Mentioned in
- [Jarvis-style personal AI operating system (LiveKit voice agent + HUD)](../../OrbiOS/Jarvis-style%20personal%20AI%20operating%20system%20%28LiveKit%20voice%20agent%20%2B%20HUD%29.md)
