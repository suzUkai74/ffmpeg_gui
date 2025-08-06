import flet as ft
from views.video import Video
from views.image import Image

def main(page: ft.Page):
    page.title = "ffmpeg GUI"
    page.scroll = ft.ScrollMode.AUTO

    video = Video(page)
    image = Image(page)

    tab = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        tabs=[
            ft.Tab(
                text="動画加工",
                icon=ft.icons.ONDEMAND_VIDEO,
                content=ft.Container(video.get_view(), padding=10),
            ),
            ft.Tab(
                text="画像座標",
                icon=ft.icons.IMAGE,
                content=ft.Container(image.get_view(), padding=10),
            ),
        ],
        unselected_label_color=ft.colors.GREY_400,
        expand=1,
        overlay_color=ft.colors.AMBER_300,
    )

    page.add(tab)
    page.update()

ft.app(main)
