# MoE expert streaming

The core hardware-minimization technique for sparse Mixture-of-Experts models: never load the "sleeping" experts a given token doesn't need — keep a small always-active dense/trunk resident in RAM, and stream only the router-selected active experts (e.g. Kimi K3's 16 of 896, ~1.8%) from disk per token, discarding them right after. RAM usage and per-token disk I/O scale with the resident trunk size and active-expert count, not total parameter count — which is why Colibri's proven range (744B–2.8T) extrapolates only modestly to a 3.5T target. Complementary mechanisms: on-demand fetch straight from packed low-bit form (no full-precision intermediate copy), an LRU/LFU cache of "hot" experts, and one-layer-ahead routing prediction to prefetch and hide disk latency. Best suited to MoE models specifically (Kimi K3); the wrong tool for dense models, which have no sparsity to exploit.

## Mentioned in
- [Kimi K3 HW Mini](../../OrbiLLM/Hardware/kimi%20k3%20hw%20mini.md)
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
- [Qwen 3.8 HW Mini](../../OrbiLLM/Hardware/qwen%203.8%20hw%20mini.md)
- [Mach 1 HW Mini](../../OrbiLLM/Hardware/mach%201%20hw%20mini.md)
