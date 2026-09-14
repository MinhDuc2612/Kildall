# kimi-k3-in-c

An open-source project (github.com/FareedKhan-dev/kimi-k3-in-c) by developer Fareed Khan that runs Moonshot AI's 2.78-trillion-parameter Kimi K3 model on a single CPU with 8GB of RAM and no GPU — 1.56TB checkpoint on disk, 8.24GB peak RSS measured, 176KB total engine size, Apache-2.0 licensed engine code (the model weights are separately licensed by Moonshot AI). Works by keeping a small dense "trunk" resident in RAM and streaming only the router-selected experts (~1.8% of the model) from NVMe SSD per token, using direct I/O and an LRU expert cache; produces byte-identical output regardless of how much RAM is given, trading only speed. Runs at roughly 26–33 seconds/token at the 8GB floor.

## Mentioned in
- [Kimi K3 HW Mini](../../OrbiLLM/Hardware/kimi%20k3%20hw%20mini.md)
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
