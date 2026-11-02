import os
import sys
import tempfile
from pathlib import Path

# Dữ liệu kiểm thử nằm trong thư mục tạm, bật engine giả lập.
_TMP = tempfile.mkdtemp(prefix="voxviet-test-")
os.environ["VOXVIET_DATA"] = _TMP
os.environ["VOXVIET_DEMO"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
