"""Tiến trình phụ chạy Chatterbox (tiếng Anh) trong môi trường Python riêng.

Chatterbox cần phiên bản torch/transformers khác lõi giọng nên được cài vào
``envs/chatterbox`` (xem install_english_pro.bat) và giao tiếp qua stdin/stdout
bằng JSON, mỗi dòng một lệnh:

    {"cmd": "synth", "text": "...", "ref": "path.wav"|null, "exaggeration": 0.5,
     "cfg_weight": 0.5, "temperature": 0.8, "out": "path.wav"}
    → {"ok": true, "sr": 24000}

File này KHÔNG import gì từ voxviet.
"""

import json
import sys
import traceback


def main():
    import torch
    import torchaudio as ta
    from chatterbox.tts import ChatterboxTTS

    device = sys.argv[1] if len(sys.argv) > 1 else ("cuda" if torch.cuda.is_available() else "cpu")
    model = ChatterboxTTS.from_pretrained(device=device)
    print(json.dumps({"ready": True, "sr": model.sr, "device": device}), flush=True)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            if req.get("cmd") == "quit":
                break
            wav = model.generate(
                req["text"],
                audio_prompt_path=req.get("ref") or None,
                exaggeration=float(req.get("exaggeration", 0.5)),
                cfg_weight=float(req.get("cfg_weight", 0.5)),
                temperature=float(req.get("temperature", 0.8)),
            )
            ta.save(req["out"], wav.cpu(), model.sr)
            print(json.dumps({"ok": True, "sr": model.sr}), flush=True)
        except Exception as e:  # trả lỗi về tiến trình chính
            print(json.dumps({"ok": False, "error": f"{e}", "trace": traceback.format_exc()[-1500:]}), flush=True)


if __name__ == "__main__":
    main()
