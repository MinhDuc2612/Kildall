#!/usr/bin/env bash
# UHWmini setup — Mac mini M4 24GB. Safe to re-run. Read before running.
set -uo pipefail
say(){ printf "\n\033[1m== %s\033[0m\n" "$1"; }

say "1. Machine"
sysctl -n machdep.cpu.brand_string; echo "RAM: $(( $(sysctl -n hw.memsize)/1073741824 )) GB"
echo "Current Metal wired limit: $(sysctl -n iogpu.wired_limit_mb 2>/dev/null || echo 'unset (= system default)') MB"

say "2. Python (need 3.10-3.12 for Soup/Unsloth)"
for p in python3 python3.12 python3.11 python3.10; do
  command -v $p >/dev/null && echo "$p -> $($p -V 2>&1)"
done

say "3. MLX"
if python3 -c 'import mlx' 2>/dev/null; then echo "mlx: installed"
else echo "mlx: MISSING -> pip install mlx-lm"; fi
command -v llama-server >/dev/null && echo "llama.cpp: installed" || echo "llama.cpp: MISSING -> brew install llama.cpp"

say "4. Memory pressure right now"
memory_pressure 2>/dev/null | tail -3 || vm_stat | head -4

say "5. THE ONE STEP THAT NEEDS YOU"
cat <<'MSG'
Raise the Metal wired-memory ceiling (UHWmini section 5b). Needs sudo:

    sudo sysctl iogpu.wired_limit_mb=20480     # 20 GB of 24; leave OS headroom

Not persistent across reboot. Raise in STEPS and test each one.
Too high = the machine hangs, not slows.
MSG

say "6. Real ceiling (authoritative)"
echo "Start llama-server once and read 'recommendedMaxWorkingSetSize' in its startup log."
echo "Use THAT number, not UHWmini's ~18-19 GB estimate."
