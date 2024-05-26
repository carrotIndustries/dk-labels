import cairo
import gi

gi.require_version("PangoCairo", "1.0")
gi.require_version("Pango", "1.0")
from gi.repository import Pango
from gi.repository import PangoCairo
import os
import qrcode

def putpixel(surf, x, y, v):
    offset = surf.get_stride() * y + x * 4
    v = 255 if v else 0
    d = surf.get_data()
    for i in range(4):
        d[offset + i] = v


def render_small_label(text, text2, qrtext=""):
    width = 320
    height = 96
    imgsurf = cairo.ImageSurface(
        cairo.Format.RGB24, width, height
    )

    ctx = cairo.Context(imgsurf)
    ctx.set_source_rgb(1,1,1)
    ctx.paint()
    ctx.translate(0, 0)
    opts = cairo.FontOptions()
    opts.set_antialias(cairo.ANTIALIAS_NONE)
    layout = PangoCairo.create_layout(ctx)
    layout.set_text(text)
    font_size = 21
    while True :
        PangoCairo.context_set_font_options(layout.get_context(), opts)
        font = Pango.FontDescription(f"Cantarell Bold {font_size}")
        layout.set_font_description(font)
        ink, log = layout.get_pixel_extents()
        if ink.width < width-20 :
            break
        else :
            font_size -= 1
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(10, 5)
    PangoCairo.show_layout(ctx, layout)
    mpn_font_size = font_size
    
    font_size = 21
    layout.set_text(text2)
    width2 = width-20
    if qrtext != "" :
        width2 = width - 65
    layout.set_width(width2*1000)
    layout.set_line_spacing(0.7)

    while True :
        font = Pango.FontDescription(f"Cantarell Bold {font_size}")
        layout.set_font_description(font)
        ink, log = layout.get_pixel_extents()
        if ink.height < height-14-mpn_font_size :
            break
        else :
            font_size -= 1
    ctx.move_to(10, mpn_font_size+8)
    PangoCairo.show_layout(ctx, layout)
    
    imgsurf.flush()
    if qrtext != "" :
        try :
            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=2,
                border=2,
            )
            qr.add_data(qrtext)
            qr.make(fit=False)

            qrimg = qr.make_image(fill_color="black", back_color="white").get_image()
            for x in range(qrimg.width):
                for y in range(qrimg.height):
                    putpixel(imgsurf, width-65 + x, height-63 + y, qrimg.getpixel((x, y)))
            imgsurf.mark_dirty()
        except qrcode.exceptions.DataOverflowError :
            pass


    return imgsurf


if __name__ == "__main__":
    imgsurf = render_small_label("JE2835AWT-R2222221", "LED J WARM WHTtt 2700K 1411", "644-CS14523-24.576MTR-ND")
    imgsurf.write_to_png("out.png")
