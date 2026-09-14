# Load mode (mmap vs mlock)

llama.cpp's `-lm`/`--load-mode` flag (replacing the deprecated `--mmap`/`--no-mmap`), controlling whether a model is memory-mapped (`mmap` — the OS pages it in on demand, letting you run a model larger than physical RAM by trading speed for capacity — the same mechanism kimi-k3-in-c's disk-streaming depends on) or force-locked into RAM (`mlock` — guarantees no swap-related stalls, at the cost of needing the full footprint resident). The direct lever for choosing "smaller footprint, accept disk-read latency" versus "predictable speed, need the RAM."

## Mentioned in
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
