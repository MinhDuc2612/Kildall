"""Nuke entry/target separation and race controls; every deletion uses a temporary tree."""

import os
from pathlib import Path
import stat
import tempfile
from unittest.mock import patch

import permissions as p


def blocked(action):
    try:
        action()
    except (PermissionError, RuntimeError, OSError):
        return
    raise AssertionError("Unsafe or changed path was accepted")


def main():
    with tempfile.TemporaryDirectory(prefix="kildall-nuke-") as temporary:
        work = Path(temporary).resolve()
        vault = work / "Kildall"
        vault.mkdir()
        outside = vault / "Researchhub"
        outside.mkdir()
        sentinel = outside / "keep.txt"
        sentinel.write_text("outside target survives")
        root = vault / "code"

        def tree():
            root.mkdir()
            (root / "nested").mkdir()
            (root / "nested/file").write_text("inside only")

        tree()
        targets = {
            "outward-directory": outside,
            "outward-file": sentinel,
            "dangling-outward": outside / "missing",
            "inward-directory": root / "nested",
            "inward-file": root / "nested/file",
            "dangling-inward": root / "missing",
            "self": Path("."),
            "loop-a": Path("loop-b"),
            "loop-b": Path("loop-a"),
        }
        for name, target in targets.items():
            (root / name).symlink_to(target)
        manifest, rejected = p.nuke_manifest(root)
        assert rejected == 0
        assert all(Path(row[0]).is_absolute() and Path(row[0]).is_relative_to(root) for row in manifest)
        assert {Path(row[0]).name for row in manifest if stat.S_ISLNK(row[3])} == set(targets)
        assert not any("keep.txt" in row[0] for row in manifest)
        p._delete_tree(root, manifest)
        assert not os.path.lexists(root)
        assert sentinel.read_text() == "outside target survives"
        assert not (outside / "missing").exists()
        print("PASS: complete throwaway deletion unlinks outward, inward, dangling and looping links without following targets")

        tree()
        outward = root / "out"
        outward.symlink_to(outside)
        inward = root / "in"
        inward.symlink_to(root / "nested")

        def open_parent(path, allow=False):
            with p.parent_fd(path, root, allow_leaf_symlink=allow) as (fd, leaf):
                return os.stat(leaf, dir_fd=fd, follow_symlinks=False)

        blocked(lambda: open_parent(outward))
        assert stat.S_ISLNK(open_parent(outward, True).st_mode)
        for candidate in (outward / "keep.txt", inward / "file", root / "../Researchhub/keep.txt",
                          sentinel, str(root).replace("Kildall", "Kildall".lower()) + "/nested/file",
                          work / "Orbi/code/nested/file", "~/outside"):
            blocked(lambda candidate=candidate: open_parent(candidate, True))
        assert open_parent(root / "nested/file").st_size == len("inside only")
        blocked(lambda: p.nuke_manifest(inward))
        p._delete_tree(root, p.nuke_manifest(root)[0])
        assert not root.exists() and sentinel.exists()
        print("PASS: optional leaf handling preserves default guard and rejects symlink ancestors, traversal, absolute, home and case escapes")

        tree()
        manifest = p.nuke_manifest(root)[0]
        (root / "new-file").write_text("new")
        blocked(lambda: p._delete_tree(root, manifest))
        assert (root / "nested/file").exists() and (root / "new-file").exists()
        p._delete_tree(root, p.nuke_manifest(root)[0])
        print("PASS: changed manifest refuses deletion before touching any entry")

        # Swap after the fresh scan, at the boundary between review and mutation.
        scan = p.nuke_manifest
        for kind in ("parent", "root", "leaf"):
            tree()
            manifest = scan(root)[0]
            moved = vault / ("retained-" + kind)

            def swap_after_scan(candidate):
                result = scan(candidate)
                if kind == "parent":
                    (root / "nested").rename(moved)
                    (root / "nested").symlink_to(outside)
                elif kind == "root":
                    root.rename(moved)
                    root.symlink_to(outside)
                else:
                    (root / "nested/file").rename(moved)
                    (root / "nested/file").symlink_to(sentinel)
                return result

            with patch.object(p, "nuke_manifest", side_effect=swap_after_scan):
                blocked(lambda: p._delete_tree(root, manifest))
            assert sentinel.read_text() == "outside target survives"
            assert (moved / "nested/file" if kind == "root" else
                    moved / "file" if kind == "parent" else moved).read_text() == "inside only"
            if kind == "root":
                root.unlink()  # Remove only the temporary alias, never its outside target.
            else:
                p._delete_tree(root, scan(root)[0])
        print("PASS: parent, root and leaf swaps after scan are refused; original entries and outside targets survive")

        tree()
        actual_open = os.open
        swapped = False

        def swap_before_descent(path, flags, *args, **kwargs):
            nonlocal swapped
            if path == "nested" and kwargs.get("dir_fd") is not None and not swapped:
                swapped = True
                (root / "nested").rename(root / "retained")
                (root / "nested").symlink_to(outside)
            return actual_open(path, flags, *args, **kwargs)

        with patch.object(p.os, "open", side_effect=swap_before_descent):
            blocked(lambda: p.nuke_manifest(root))
        assert swapped and (root / "retained/file").read_text() == "inside only"
        assert sentinel.read_text() == "outside target survives"
        p._delete_tree(root, scan(root)[0])
        assert not root.exists()
        print("PASS: directory swap between lstat and descent fails O_NOFOLLOW")

    print("PASS: nuke controls completed using temporary trees only; production root unchanged")


if __name__ == "__main__":
    main()
