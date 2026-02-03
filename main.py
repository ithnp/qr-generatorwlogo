import io
import os
from datetime import datetime  # <-- ADD
import requests
import qrcode
from PIL import Image, ImageDraw

from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask

# =========================
# CONFIG
# =========================
QR_LINK = "https://google.com"
LOGO_SOURCE = "C:/Users/user/Pictures/sample-logo.png"  # atau URL

OUTPUT_DIR = "output_qr"       # <-- folder output (bisa absolute path juga)
OUTPUT_FILE = "qr_barcode.png" # <-- nama file output

BOX_SIZE = 18
BORDER = 6
MIN_VERSION = 10

# logo config
LOGO_SCALE = 0.20
WHITE_PAD_RATIO = 0.22

# logo rounding
PAD_SHAPE = "rounded"          # "circle" atau "rounded"
PAD_RADIUS_RATIO = 0.13        # hanya dipakai kalau PAD_SHAPE="rounded"
PAD_MARGIN_PX = 0              # kalau mau pad sedikit lebih kecil: misal 4 atau 8

# style: pilih salah satu
STYLE = "rounded"   # "rounded" atau "dots"

# warna QR
FRONT_COLOR = (0, 0, 0)
BACK_COLOR = (255, 255, 255)
# =========================


def load_logo(source: str) -> Image.Image:
    if source.startswith("http://") or source.startswith("https://"):
        r = requests.get(source, timeout=20)
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content)).convert("RGBA")
    return Image.open(source).convert("RGBA")


def snap_to_grid(v: float, grid: int) -> int:
    return int(round(v / grid) * grid)


def make_logo_rounded(logo: Image.Image, mode="rounded", radius_ratio=0.25) -> Image.Image:
    """
    mode:
      - "circle"  : logo jadi lingkaran
      - "rounded" : logo jadi rounded-rectangle
    radius_ratio: untuk mode "rounded" (0.2 - 0.35 enak)
    """
    logo = logo.convert("RGBA")
    w, h = logo.size

    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)

    if mode == "circle":
        d.ellipse((0, 0, w, h), fill=255)
    else:
        r = int(min(w, h) * radius_ratio)
        d.rounded_rectangle((0, 0, w, h), radius=r, fill=255)

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(logo, (0, 0), mask)
    return out


def make_styled_qr(link: str):
    qr = qrcode.QRCode(
        version=MIN_VERSION,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=BOX_SIZE,
        border=BORDER,
    )
    qr.add_data(link)
    qr.make(fit=True)

    n_data = len(qr.get_matrix())

    if STYLE == "rounded":
        module_drawer = RoundedModuleDrawer()
    else:
        module_drawer = CircleModuleDrawer()

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=module_drawer,
        color_mask=SolidFillColorMask(front_color=FRONT_COLOR, back_color=BACK_COLOR)
    ).convert("RGBA")

    return img, n_data


def punch_out_center_pixel(qr_img: Image.Image, n_data: int):
    img_w, img_h = qr_img.size

    logo_modules = max(9, int(n_data * LOGO_SCALE))
    if logo_modules % 2 == 0:
        logo_modules += 1

    box_px = logo_modules * BOX_SIZE

    x0 = (img_w - box_px) / 2
    y0 = (img_h - box_px) / 2

    # snap ke grid modul
    x0 = snap_to_grid(x0, BOX_SIZE)
    y0 = snap_to_grid(y0, BOX_SIZE)

    x1 = x0 + box_px
    y1 = y0 + box_px

    # NOTE: tidak menggambar rectangle putih lagi
    return qr_img, (x0, y0, x1, y1)


def place_logo(qr_img: Image.Image, logo: Image.Image, bbox):
    x0, y0, x1, y1 = bbox
    box_w, box_h = x1 - x0, y1 - y0

    # Optional: kecilkan sedikit area pad biar lebih rapi
    m = max(0, int(PAD_MARGIN_PX))
    box_w2 = box_w - 2 * m
    box_h2 = box_h - 2 * m

    # Buat layer pad (transparan) + shape mask
    pad = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    mask = Image.new("L", (box_w, box_h), 0)

    d_pad = ImageDraw.Draw(pad)
    d_mask = ImageDraw.Draw(mask)

    if PAD_SHAPE == "circle":
        shape_box = (m, m, m + box_w2, m + box_h2)
        d_pad.ellipse(shape_box, fill=(255, 255, 255, 255))
        d_mask.ellipse(shape_box, fill=255)
    else:
        shape_box = (m, m, m + box_w2, m + box_h2)
        radius = int(min(box_w2, box_h2) * PAD_RADIUS_RATIO)
        d_pad.rounded_rectangle(shape_box, radius=radius, fill=(255, 255, 255, 255))
        d_mask.rounded_rectangle(shape_box, radius=radius, fill=255)

    # 1) blank QR sesuai SHAPE (bukan kotak)
    out = qr_img.copy()
    white_layer = Image.new("RGBA", (box_w, box_h), (255, 255, 255, 255))
    out.paste(white_layer, (x0, y0), mask)

    # 2) tempel pad putih (agar tepi anti-aliasing halus)
    out.paste(pad, (x0, y0), pad)

    # logo size (di dalam pad)
    inner_w = int(box_w2 * (1 - WHITE_PAD_RATIO))
    inner_h = int(box_h2 * (1 - WHITE_PAD_RATIO))

    logo = logo.copy().convert("RGBA")
    logo.thumbnail((inner_w, inner_h), Image.LANCZOS)

    # paste logo ke tengah pad
    lx = x0 + m + (box_w2 - logo.size[0]) // 2
    ly = y0 + m + (box_h2 - logo.size[1]) // 2
    out.paste(logo, (lx, ly), logo)

    return out


if __name__ == "__main__":
    qr_img, n_data = make_styled_qr(QR_LINK)
    punched, bbox = punch_out_center_pixel(qr_img, n_data)
    logo = load_logo(LOGO_SOURCE)
    final = place_logo(punched, logo, bbox)

    # ====== SAVE TO FOLDER (WITH TIMESTAMP) ======
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")  # aman untuk Windows (tanpa ':')
    name, ext = os.path.splitext(OUTPUT_FILE)
    output_filename = f"{name}_{ts}{ext}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    final.save(output_path)
    print("OK:", output_path)
