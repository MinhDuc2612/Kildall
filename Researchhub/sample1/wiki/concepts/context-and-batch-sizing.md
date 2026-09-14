# Context and batch sizing

The most basic hardware-minimization lever and the one people skip: context size (`-c`/`--ctx-size` in llama.cpp) directly multiplies KV cache cost, and batch/micro-batch size (`-b`/`-ub`) trade throughput for peak memory during prompt processing. Setting `--ctx-size` to only what's actually needed, rather than the model's max, is free memory savings with zero quality cost.

## Mentioned in
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
