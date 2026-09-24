"""On-demand Markdown instruction packs; declarations never grant permissions."""
import os
from pathlib import Path
import re
import stat

import yaml
from shell_tools import tool

TOOL = tool('load_skill', 'Load a named instruction pack. Required tools do not grant permission.',
            dict(name=dict(type='string')), ['name'])


class SkillLoader(yaml.SafeLoader):
    pass


def mapping(loader, node):
    pairs = loader.construct_pairs(node)
    result = {}
    for key, value in pairs:
        if not isinstance(key, str) or key in result:
            raise ValueError('Skill metadata requires unique string keys')
        result[key] = value
    return result


SkillLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def slug(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value) or len(value) > 80:
        raise ValueError('Skill names use lowercase letters, digits and hyphens')
    return value


def packs(project, available_names, *, global_root=None, project_root=None):
    from permissions import CODE_ROOT, parent_fd
    roots = [('global', Path(global_root) if global_root is not None else CODE_ROOT / 'skills'),
             ('project', Path(project_root) if project_root is not None else Path(project).resolve() / '.orbi/skills')]
    found = {}
    for source, root in roots:
        root = root.absolute()
        if str(root) != os.path.realpath(root):
            raise PermissionError('Skill directory must not redirect through symlinks')
        try:
            entries = list(os.scandir(root))
        except FileNotFoundError:
            continue
        for entry in sorted(entries, key=lambda e: e.name):
            if entry.is_symlink():
                raise PermissionError('Symlinked skill directories are forbidden')
            if not entry.is_dir(follow_symlinks=False):
                continue
            path = Path(entry.path) / 'SKILL.md'
            try:
                with parent_fd(path, root) as (directory, name):
                    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
            except FileNotFoundError:
                continue
            with os.fdopen(fd, 'rb') as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise PermissionError('Skill must be a regular file')
                raw = stream.read(32769)
            if len(raw) > 32768:
                raise ValueError('Skill exceeds 32 KiB')
            text = raw.decode('utf-8')
            parts = text.split('---\n', 2)
            if len(parts) != 3 or parts[0] or not parts[2].strip():
                raise ValueError('Skill requires YAML frontmatter and instructions')
            # No aliases: bounded text must not become recursive or amplified metadata.
            try:
                if any(isinstance(token, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken)) for token in yaml.scan(parts[1])):
                    raise ValueError('YAML aliases are not supported')
                metadata = yaml.load(parts[1], Loader=SkillLoader)
            except yaml.YAMLError as error:
                raise ValueError('Invalid skill metadata') from error
            if not isinstance(metadata, dict) or set(metadata) != {'name', 'description', 'tools'}:
                raise ValueError('Skill requires exactly name, description and tools')
            name = slug(metadata['name'])
            if name != entry.name or not isinstance(metadata['description'], str) or not metadata['description'].strip():
                raise ValueError('Skill name must match its directory; description must be nonempty')
            needs = metadata['tools']
            if not isinstance(needs, list) or any(not isinstance(t, str) or t not in available_names for t in needs) or len(set(needs)) != len(needs):
                raise ValueError('Skill tools must be a unique list of available tools')
            found[name] = dict(metadata, source=source, path=str(path), instructions=parts[2])
    return found


def discover(project, available_names, **roots):
    return [{k: v for k, v in pack.items() if k != 'instructions'}
            for _, pack in sorted(packs(project, available_names, **roots).items())]


def load(name, project, available_names, **roots):
    slug(name)
    found = packs(project, available_names, **roots)
    if name not in found:
        raise ValueError('No such instruction skill: ' + name)
    return dict(found[name], permissions='Tool requirements only; normal executor permissions and explicit Git intent still apply.')
