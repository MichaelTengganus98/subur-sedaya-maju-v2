"""Generate WebP siblings for the raster photos in static/images/.

Usage:
    python manage.py optimize_images          # only missing / stale ones
    python manage.py optimize_images --force  # rebuild all
    python manage.py optimize_images --max-width 1600 --quality 80

The templates reference the WebP via a <picture><source> (see
templates/partials/_picture.html); the original file stays as the <img>
fallback, so it is safe to run or skip this at any time.
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

# Big content photos only. Logos (transparency) and tiny UI icons are left as-is.
TARGETS = [
    "hero-truck.jpeg",
    "visi-photo.png",
    "partner-photo.png",
    "mitra-photo.jpeg",
]


class Command(BaseCommand):
    help = "Create optimized WebP versions of the site photos in static/images/."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Rebuild even if up to date.")
        parser.add_argument("--max-width", type=int, default=1800, help="Downscale wider images to this width.")
        parser.add_argument("--quality", type=int, default=80, help="WebP quality (0-100).")

    def handle(self, *args, **opts):
        try:
            from PIL import Image
        except ImportError:
            self.stderr.write("Pillow is not installed (it is in requirements.txt).")
            return

        img_dir = Path(settings.BASE_DIR) / "static" / "images"
        force, max_w, quality = opts["force"], opts["max_width"], opts["quality"]
        total_before = total_after = 0

        for name in TARGETS:
            src = img_dir / name
            if not src.exists():
                self.stderr.write(f"skip (missing): {name}")
                continue
            dst = src.with_suffix(".webp")
            if dst.exists() and not force and dst.stat().st_mtime >= src.stat().st_mtime:
                self.stdout.write(f"up to date: {dst.name}")
                continue

            with Image.open(src) as im:
                im = im.convert("RGB")
                if im.width > max_w:
                    h = round(im.height * max_w / im.width)
                    im = im.resize((max_w, h), Image.LANCZOS)
                im.save(dst, "WEBP", quality=quality, method=6)

            before, after = src.stat().st_size, dst.stat().st_size
            total_before += before
            total_after += after
            self.stdout.write(
                self.style.SUCCESS(
                    f"{src.name} {before // 1024} KB  ->  {dst.name} {after // 1024} KB"
                )
            )

        if total_before:
            saved = (total_before - total_after) / 1024
            self.stdout.write(self.style.SUCCESS(f"Total saved: {saved:.0f} KB"))
