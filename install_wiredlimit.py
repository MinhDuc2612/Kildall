"""Print the boot-daemon installation commands for the user; never execute sudo."""

from pathlib import Path
from kildall_platform import jobs


def main():
    jobs().print_wiredlimit_install(
        Path(__file__).resolve().parent / "launchd/local.kildall.wiredlimit.plist")


if __name__ == "__main__":
    main()
