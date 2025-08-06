import flet as ft
import os
from PIL import Image

class MapEditor:
    def __init__(self, page: ft.Page):
        self.start = None
        self.end = None
        self.page = page
        self.rects = []
        self.selected = None
        self.preview = ft.Container(visible=False, border=ft.border.all(1,"blue"), bgcolor="rgba(0,0,255,0.3)")
        self.stack = None
        self.img_path = ""
        self.img_width = 0
        self.img_height = 0
        self.min_drag_distance = 10

    def reset(self):
        self.start = None
        self.end = None
        self.rects.clear()
        self.selected = None
        self.stack = None
        self.preview = ft.Container(visible=False, border=ft.border.all(1, "blue"), bgcolor="rgba(0,0,255,0.3)")

    def load_image(self, path):
        self.reset()
        self.img_path = path
        with Image.open(path) as img:
            self.img_width, self.img_height = img.size

        self.preview = ft.Container(visible=False, border=ft.border.all(1,"blue"), bgcolor="rgba(0,0,255,0.3)")

        self.stack = ft.Stack(
            width=self.img_width,
            height=self.img_height,
            alignment=ft.alignment.center,
            controls=[
                ft.Image(src=f"/{path}", width=self.img_width, height=self.img_height),
                self.preview,
                ft.GestureDetector(
                    content=ft.Container(width=self.img_width, height=self.img_height, bgcolor="transparent"),
                    on_pan_start=self.down,
                    on_pan_update=self.move,
                    on_pan_end=self.up
                )
            ]
        )

    def down(self, e):
        self.start = (e.local_x, e.local_y)
        self.preview.left = e.local_x
        self.preview.top = e.local_y
        self.preview.width = 1
        self.preview.height = 1
        self.preview.visible = True
        self.stack.update()

    def move(self, e):
        if self.start:
            x1, y1 = self.start
            x2, y2 = e.local_x, e.local_y
            self.end = (x2, y2)
            self.preview.left = min(x1, x2)
            self.preview.top = min(y1, y2)
            self.preview.width = abs(x2 - x1)
            self.preview.height = abs(y2 - y1)
            self.stack.update()

    def up(self, e):
        if self.start and self.end:
            x1, y1 = self.start
            x2, y2 = self.end
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)

            if dx < self.min_drag_distance or dy < self.min_drag_distance:
                self.preview.visible = False
                self.stack.update()
                self.start = None
                return

            rect = {
                "x": self.preview.left,
                "y": self.preview.top,
                "w": self.preview.width,
                "h": self.preview.height,
                "container": None
            }
            cont = ft.Container(
                left=rect["x"], top=rect["y"],
                width=rect["w"], height=rect["h"],
                border=ft.border.all(2, "blue"),
                bgcolor="rgba(255,0,0,0.3)",
                on_click=lambda e, r=rect: self.select(r)
            )
            rect["container"] = cont
            self.rects.append(rect)
            self.stack.controls.append(cont)
            self.preview.visible = False
            self.start = None
            self.end = None
            self.stack.update()

    def select(self, rect):
        for r in self.rects:
            if r is rect:
                r["container"].border = ft.border.all(2, "red")
                r["container"].bgcolor = "rgba(255,0,0,0.3)"
            else:
                r["container"].border = ft.border.all(2, "blue")
                r["container"].bgcolor = "rgba(0,0,255,0.3)"
        self.selected = rect
        self.stack.update()

    def delete_selected(self, _):
        if self.selected:
            self.stack.controls.remove(self.selected["container"])
            self.rects.remove(self.selected)
            self.selected = None
            self.stack.update()

    def output_imagemap(self):
        lines = []
        for r in self.rects:
            x1 = int(r["x"])
            y1 = int(r["y"])
            x2 = x1 + int(r["w"])
            y2 = y1 + int(r["h"])
            lines.append(f'<area shape="rect" coords="{x1},{y1},{x2},{y2}" href="#" />')
        return "\n".join(lines)

    def build_ui(self):
        return [
            ft.Row([
                ft.ElevatedButton("矩形を削除", on_click=self.delete_selected),
                ft.ElevatedButton("イメージマップ出力", on_click=lambda e: self.show_output())
            ]),
            self.stack if self.stack else ft.Text("画像を読み込んでください")
        ]

    def show_output(self):
        result = self.output_imagemap()
        dialog = ft.AlertDialog(
            title=ft.Text("HTML イメージマップ"),
            content=ft.Text(result),
            on_dismiss=lambda e: None
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
