"""Kildall-27b recall gate: the frozen test_recall.py, unchanged, against the 27b runtime (ports 8423/8424).

The frozen file names 8123 for generation. This wrapper only redirects that URL to the configured 8423 runtime;
memory.py in this copy already embeds on 8424. It starts and stops the 27b runtime itself, checks the frozen
file's bytes first, and passes only on 20/20 (the standing gate), not on the frozen file's own threshold.
"""
import hashlib, inspect, json, sys, urllib.request
from pathlib import Path
from unittest.mock import patch

import benchmark, kildall, memory, test_recall

FROZEN_SHA256 = 'ae83425c9cd3a569403c50d7ee95eb6a90a3569d1062856aecf50af52fb2387d'
FROZEN_URL = 'http://127.0.0.1:8123'


def main():
    digest = hashlib.sha256(Path(test_recall.__file__).read_bytes()).hexdigest()
    assert digest == FROZEN_SHA256, f'frozen test_recall.py changed: {digest}'
    config = kildall.settings()
    target = kildall.url(config)
    assert target != FROZEN_URL and config['runtime']['parallel'] == 1, (target, config['runtime']['parallel'])
    # The frozen file builds Memory(...) with the default embedding URL; it must be this runtime's Harrier port.
    embedding = inspect.signature(memory.Memory.__init__).parameters['embedding_url'].default
    assert embedding == kildall.url(config, embedding=True) + '/v1/embeddings', embedding
    real_open = urllib.request.urlopen

    def redirect(url, *args, **kwargs):  # Only the frozen /slots check passes a bare 8123 string here.
        return real_open(url.replace(FROZEN_URL, target) if isinstance(url, str) else url, *args, **kwargs)

    kildall.ensure_runtime(config)
    try:
        with patch.object(test_recall, 'chat', lambda url, *a, **k: benchmark.chat(url.replace(FROZEN_URL, target), *a, **k)), \
                patch.object(urllib.request, 'urlopen', redirect):
            code = test_recall.main()
    finally:
        kildall.ensure_runtime(config, stop=True)
    results = json.loads((Path(test_recall.__file__).parent / '.session' / 'recall-results.json').read_text())
    print(json.dumps(dict(frozen_exit=code, score=results.get('score'), target=target, frozen_sha256=digest)), flush=True)
    return 0 if code == 0 and results.get('score') == 20 else 1


if __name__ == '__main__':
    sys.exit(main())
