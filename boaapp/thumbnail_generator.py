"""
AI-powered thumbnail generation for notebooks/courses.
Uses Pillow to create styled thumbnails with dynamic content.
Falls back to HTML-to-image style generation if DALL-E is not available.
"""

import logging
import os
import random
from pathlib import Path

from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Gradient color palettes for thumbnails
PALETTES = [
    [(59, 130, 246), (99, 102, 241)],  # Blue → Indigo
    [(16, 185, 129), (6, 182, 212)],  # Emerald → Cyan
    [(168, 85, 247), (236, 72, 153)],  # Purple → Pink
    [(249, 115, 22), (234, 179, 8)],  # Orange → Amber
    [(239, 68, 68), (236, 72, 153)],  # Red → Pink
    [(20, 184, 166), (59, 130, 246)],  # Teal → Blue
]


def generate_thumbnail(document_id, title=None, subtitle=None):
    """
    Generate a styled thumbnail image for a document.
    Returns the absolute path to the generated thumbnail.
    """
    from .models import CourseThumbnail, Document

    doc = Document.objects.get(pk=document_id)

    if not title:
        # Extract title from notebook filename
        stem = Path(doc.uploaded_file.name).stem
        import re

        title = re.sub(r'^\d+[\s_-]+', '', stem).replace('-', ' ').replace('_', ' ')

    if not subtitle:
        subtitle = 'thenumerix | AI-Powered Learning'

    # Generate the image
    img = _create_gradient_thumbnail(title, subtitle)

    # Save to media/thumbnails/
    thumbnails_dir = Path(settings.MEDIA_ROOT) / 'thumbnails'
    thumbnails_dir.mkdir(parents=True, exist_ok=True)

    filename = f'thumb_{document_id}.png'
    filepath = thumbnails_dir / filename

    img.save(str(filepath), 'PNG', quality=95)
    logger.info(f'Generated thumbnail for document {document_id}: {filepath}')

    # Save or update DB record
    relative_path = f'thumbnails/{filename}'
    thumb, created = CourseThumbnail.objects.update_or_create(
        document=doc,
        defaults={
            'image': relative_path,
            'prompt_used': f'Title: {title}, Subtitle: {subtitle}',
        },
    )

    return str(filepath)


def _create_gradient_thumbnail(title, subtitle, width=1280, height=720):
    """Create a gradient background thumbnail with text overlay."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Pick random palette
    palette = random.choice(PALETTES)
    c1, c2 = palette

    # Draw gradient
    for y in range(height):
        ratio = y / height
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Add decorative elements
    _draw_decorations(draw, width, height)

    # Find available fonts
    title_font = _get_font(size=64, bold=True)
    subtitle_font = _get_font(size=28)
    badge_font = _get_font(size=22, bold=True)

    # Draw "AI GENERATED" badge
    badge_text = 'AI GENERATED'
    badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    badge_w = badge_bbox[2] - badge_bbox[0] + 24
    badge_h = badge_bbox[3] - badge_bbox[1] + 12
    badge_x = width - badge_w - 40
    badge_y = 30
    draw.rounded_rectangle(
        [(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)],
        radius=6,
        fill=(255, 255, 255, 80),
    )
    draw.text((badge_x + 12, badge_y + 4), badge_text, fill='white', font=badge_font)

    # Draw title (word-wrapped)
    _draw_wrapped_text(draw, title, title_font, width - 120, 60, height // 2 - 80, fill='white')

    # Draw subtitle
    draw.text((60, height - 80), subtitle, fill=(255, 255, 255, 200), font=subtitle_font)

    # Draw bottom accent line
    draw.rectangle([(60, height - 40), (width - 60, height - 36)], fill=(255, 255, 255, 100))

    return img


def _draw_decorations(draw, width, height):
    """Add subtle geometric decorations."""
    # Circles
    for _ in range(5):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(40, 120)
        draw.ellipse(
            [(x - r, y - r), (x + r, y + r)],
            outline=(255, 255, 255, 20),
            width=2,
        )

    # Diagonal lines
    for _ in range(3):
        x1 = random.randint(0, width)
        draw.line(
            [(x1, 0), (x1 + 200, height)],
            fill=(255, 255, 255, 15),
            width=1,
        )


def _draw_wrapped_text(draw, text, font, max_width, x, y, fill='white'):
    """Draw text that wraps within max_width."""
    words = text.split()
    lines = []
    current_line = ''

    for word in words:
        test_line = f'{current_line} {word}'.strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Draw each line with shadow
    line_height = font.size + 10 if hasattr(font, 'size') else 74
    for i, line in enumerate(lines[:3]):  # Max 3 lines
        ly = y + i * line_height
        # Shadow
        draw.text((x + 2, ly + 2), line, fill=(0, 0, 0, 100), font=font)
        # Main text
        draw.text((x, ly), line, fill=fill, font=font)


def _get_font(size=32, bold=False):
    """Try to load a good font, falling back to default."""
    font_names = [
        'Inter-Bold.ttf' if bold else 'Inter-Regular.ttf',
        'arial.ttf',
        'ArialBD.ttf' if bold else 'arial.ttf',
        'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',
    ]

    # Check common font locations
    font_dirs = [
        'C:/Windows/Fonts',
        '/usr/share/fonts/truetype',
        '/usr/share/fonts',
    ]

    for d in font_dirs:
        for name in font_names:
            path = os.path.join(d, name)
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue

    return ImageFont.load_default()
