import json, glob, numpy as np
from pathlib import Path

data_dir = Path(r"c:\Users\rutur\OneDrive\Desktop\jotex\Dataset\ocr")
vocab = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -.,!?()[]{}:;\'\"')

total, oov_total, empty_img, label_lens, oov_chars_seen = 0, 0, 0, [], set()
for ds in ["iiit5k","synthtext","indic_scene_text"]:
    ann_dir = data_dir / ds / "annotations"
    img_dir = data_dir / ds / "images"
    for f in list(glob.glob(str(ann_dir / "*.json")))[:500]:
        data = json.load(open(f, encoding="utf-8"))
        stem = Path(f).stem
        img_p = img_dir / (stem+".jpg")
        if not img_p.exists(): img_p = img_dir / (stem+".png")
        if not img_p.exists(): empty_img += 1
        for e in data.get("entities",[]):
            t = e.get("text","")
            if not t: continue
            total += 1
            oov = [c for c in t if c not in vocab]
            oov_total += len(oov)
            oov_chars_seen.update(oov)
            label_lens.append(len(t))

print(f"Total labels: {total}")
print(f"OOV chars: {oov_total}")
print(f"OOV char set (hex): {[hex(ord(c)) for c in sorted(oov_chars_seen)][:30]}")
print(f"Missing images: {empty_img}")
print(f"Label len: min={min(label_lens)} max={max(label_lens)} mean={np.mean(label_lens):.1f}")
print(f"Labels > 20 chars (risky for CTC): {sum(l>20 for l in label_lens)}")

# Check CTC feasibility: seq_len must be >= label_len
# CRNN output seq_len = 33 for 128px wide input
ctc_seq_len = 33
print(f"Labels incompatible with CTC (len > {ctc_seq_len}): {sum(l > ctc_seq_len for l in label_lens)}")
