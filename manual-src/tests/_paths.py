"""Where the app is, for every test: the repository's own tilesmith-desktop folder, found from this file, so the tests run
from any checkout (they used to name /home/claude/tilesmith-desktop). TILESMITH_DESKTOP overrides it."""
import os
TS_DESK = os.environ.get('TILESMITH_DESKTOP') or os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tilesmith-desktop'))
TS_APP_FILE = os.path.join(TS_DESK, 'app', 'index.html')
TS_APP_URL = 'file://' + TS_APP_FILE
