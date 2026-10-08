"""Print the boot-daemon installation commands for the user; never execute sudo."""

from pathlib import Path
import shlex
import subprocess


def main():
    source = Path(__file__).resolve().parent / "launchd/local.kildall.wiredlimit.plist"
    subprocess.run(["/usr/bin/plutil", "-lint", str(source)], check=True,
                   stdout=subprocess.DEVNULL)
    target = Path("/Library/LaunchDaemons/local.kildall.wiredlimit.plist")
    service = "system/local.kildall.wiredlimit"
    existing = subprocess.run(["/bin/launchctl", "print", service], capture_output=True)
    commands = []
    if existing.returncode == 0:
        commands.append(["sudo", "/bin/launchctl", "bootout", service])
    commands.extend([
        ["sudo", "/usr/bin/install", "-o", "root", "-g", "wheel", "-m", "0644", str(source), str(target)],
        ["sudo", "/bin/launchctl", "bootstrap", "system", str(target)],
        ["sudo", "/bin/launchctl", "kickstart", service],
    ])
    for command in commands:
        print(shlex.join(command))


if __name__ == "__main__":
    main()
