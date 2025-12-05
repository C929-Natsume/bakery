#!"C:\Users\lyy\Downloads\july_client (3)\server\.venv3\Scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'qiniu==7.2.10','console_scripts','qiniupy'
__requires__ = 'qiniu==7.2.10'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('qiniu==7.2.10', 'console_scripts', 'qiniupy')()
    )
