import flet as ft
from views.video import Video
from views.image import Image
from views.pdf_compression import PdfCompression
from views.pdf_combine import PdfCombine

def main(page: ft.Page):
    page.title = "ffmpeg GUI"
    page.scroll = ft.ScrollMode.AUTO

    views = [
        ("動画加工", ft.icons.ONDEMAND_VIDEO, Video(page)),
        ("PDF圧縮", ft.icons.PICTURE_AS_PDF, PdfCompression(page)),
        ("PDF結合", ft.icons.PICTURE_AS_PDF, PdfCombine(page)),
        ("画像座標", ft.icons.IMAGE, Image(page)),
    ]

    tab = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        tabs=[
            ft.Tab(
                text=text,
                icon=icon,
                content=ft.Container(view.get_view(), padding=10),
            )
            for text, icon, view in views
        ],
        unselected_label_color=ft.colors.GREY_400,
        expand=1,
        overlay_color=ft.colors.AMBER_300,
    )

    page.add(tab)
    page.update()

ft.app(main)
