# HOBBIT

A 2024 research project ("A Mixed Precision Expert Offloading System for Fast MoE Inference," arXiv:2411.01433) that adds token-level dynamic expert loading, layer-level adaptive prefetching (predicting which experts the next layer will need while the current layer still computes), and a multidimensional expert caching policy — the same prefetch-to-hide-latency idea kimi-k3-in-c's LRU cache is described as a simpler version of.

## Mentioned in
- [Kimi K3 HW Mini](../../OrbiLLM/Hardware/kimi%20k3%20hw%20mini.md)
