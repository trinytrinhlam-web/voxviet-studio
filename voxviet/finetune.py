"""Fine-tune (LoRA) VieNeu-TTS v3 Turbo bằng giọng của bạn — module phụ, không bắt buộc.

Clone tức thì (3–8 giây mẫu) đã đủ dùng hằng ngày. Fine-tune giúp giọng giống hơn
khi bạn có 10–30 phút thu âm sạch. Cần GPU NVIDIA ~6 GB (dùng --grad-checkpoint).

Quy trình dùng mã huấn luyện chính thức của VieNeu-TTS (cài bằng install_finetune.bat
vào ``tools/VieNeu-TTS``):
  1. prepare_dataset.py  — mã hoá âm thanh → train.parquet
  2. train_lora.py --merge — huấn luyện + gộp → finetune/output/<tên>/merged
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterator

from . import paths

REPO_DIR = paths.TOOLS / "VieNeu-TTS"


def status() -> tuple[bool, str]:
    if not (REPO_DIR / "finetune" / "train_lora.py").exists():
        return False, "Chưa cài bộ fine-tune. Chạy install_finetune.bat (cần Internet, ~5 GB)."
    if not shutil.which("uv") and not (Path.home() / ".local" / "bin" / "uv.exe").exists():
        return False, "Không tìm thấy 'uv'. Chạy lại install_finetune.bat."
    return True, f"Bộ fine-tune sẵn sàng tại {REPO_DIR}"


def _uv() -> str:
    return shutil.which("uv") or str(Path.home() / ".local" / "bin" / ("uv.exe" if os.name == "nt" else "uv"))


def _run(args: list[str]) -> Iterator[str]:
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    proc = subprocess.Popen(args, cwd=str(REPO_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace", creationflags=flags, env=env)
    for line in proc.stdout:
        yield line.rstrip("\n")
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"Lệnh thất bại (mã {code}): {' '.join(args[:4])}…")


def output_dir(run_name: str) -> Path:
    return REPO_DIR / "finetune" / "output" / run_name


def train(dataset_dir: Path, run_name: str, epochs: float = 3.0, rank: int = 16,
          low_vram: bool = True) -> Iterator[str]:
    """Chạy toàn bộ quy trình, trả về từng dòng log."""
    ok, msg = status()
    if not ok:
        raise RuntimeError(msg)
    dataset_dir = Path(dataset_dir).resolve()
    if not (dataset_dir / "metadata.csv").exists():
        raise RuntimeError("Phiên thu chưa có metadata.csv — hãy thu ít nhất vài câu.")
    uv = _uv()
    yield "── Bước 1/2: chuẩn bị dữ liệu (mã hoá âm thanh) ──"
    yield from _run([uv, "run", "python", "finetune/prepare_dataset.py", "--dataset-dir", str(dataset_dir)])
    yield "── Bước 2/2: huấn luyện LoRA + gộp mô hình ──"
    args = [uv, "run", "python", "finetune/train_lora.py", "--data", str(dataset_dir / "train.parquet"),
            "--run", run_name, "--epochs", str(epochs), "--r", str(rank), "--alpha", str(rank * 2), "--merge"]
    if low_vram:
        args += ["--grad-checkpoint", "--batch-size", "2", "--grad-accum", "8"]
    yield from _run(args)
    merged = output_dir(run_name) / "merged"
    yield f"✅ Xong! Mô hình: {merged}"
