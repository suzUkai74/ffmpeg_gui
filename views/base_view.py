import flet as ft
import os

class BaseView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.ref = ft.Ref[ft.Column]()

    def get_view(self):
        return self.view

    def label_text(self, text):
        return ft.Text(f"{text}：", width=150)

    def escape_for_zsh(self, str):
        return str.replace(" ", r"\ ")

    def content_size(self, path):
        size = os.path.getsize(path)
        if size == 0:
            return "0B"

        size = round(size / 1024 ** 2, 2)
        return f"{size}MB"
    
