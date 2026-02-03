# QR Code Generator (Rounded Style + Center Logo)

Python script untuk membuat QR Code yang:
- Tetap **scannable** (Error Correction H)
- Punya style modul **rounded / dots**
- Memiliki **logo brand di tengah**
- Memakai **white pad** berbentuk **circle / rounded** agar terlihat premium
- Output otomatis tersimpan ke **folder output**

---

## ✨ Features
- ✅ QR code tetap bisa di-scan walaupun ada logo (Error Correction: `H`)
- ✅ Style QR: `rounded` atau `dots`
- ✅ White pad di tengah bisa:
  - `circle`
  - `rounded`
- ✅ Logo bisa dari:
  - file lokal
  - URL (online resource)
- ✅ Output tersimpan otomatis ke folder

---

## 📌 Requirements
- Python 3.8+
- Library:
  - `qrcode`
  - `pillow`
  - `requests`

---

## 📦 Installation

Clone repo:
```bash
git clone https://github.com/ithnp/qr-generatorwlogo.git
cd REPO_NAME

######################################### Edit bagian Config #########################################
QR_LINK = "https://google.com"
LOGO_SOURCE = "C:/Users/user/Pictures/main-logo.png"  # atau URL

OUTPUT_DIR = "output_qr"
OUTPUT_FILE = "qr_barcode.png"

STYLE = "rounded"   # "rounded" atau "dots"
PAD_SHAPE = "rounded"  # "circle" atau "rounded"


######################################### Jalankan Script #########################################
python main.py

######################################### Hasil output akan tersimpan di folder #########################################
output_qr/qr_barcode.png
