import flet as ft
from .map_editor import MapEditor
from .base_view import BaseView

class Image(BaseView):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.pick_file = ft.FilePicker(on_result=self.pick_files_result)
        self.editor = MapEditor(page)
        self.image_input_button = ft.ElevatedButton(
                                    "画像を選択",
                                    icon=ft.icons.UPLOAD_FILE,
                                    on_click=lambda _: self.pick_file.pick_files(allow_multiple=False)
                                  )
        self.view_items = [
            ft.Row(
                [
                    self.label_text("画像"),
                    self.image_input_button,
                ],
                scroll=ft.ScrollMode.AUTO
            ),
        ]
        self.set_view
        self.page.overlay.extend([self.pick_file])

    def pick_files_result(self, e: ft.FilePickerResultEvent):
      if e.files:
          src = e.files[0].path
          self.editor.load_image(src)
          self.ref.current.controls.clear()
          self.page.overlay.clear()
          self.page.overlay.append(self.pick_file)
          self.ref.current.controls.extend([
              ft.ElevatedButton("画像を変更", on_click=lambda _: self.pick_file.pick_files(allow_multiple=False)),
          ])
          self.ref.current.controls.extend(self.editor.build_ui())
          self.ref.current.update()

