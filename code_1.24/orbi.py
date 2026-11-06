"""One-release Python compatibility alias; both names share identical state."""
import sys
import kildall

if __name__ == "__main__":
    raise SystemExit(kildall.main())
sys.modules[__name__] = kildall
