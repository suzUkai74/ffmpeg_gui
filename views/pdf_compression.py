import flet as ft
from .command_view import CommandView

PDF_QUALITIES = {
    "低": "screen",
    "中": "ebook",
    "高": "printer",
    "最高": "prepress",
}

class PdfCompression(CommandView):
    output_name_label = "保存PDF名"
    output_extension = "pdf"
    created_message = "PDFが作成されました。"

    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.pick_file = ft.FilePicker(on_result=self.pick_files_result)
        self.selected_file = ft.Text()
        self.quality = ft.Dropdown(
            options=self.get_quality_options(),
            value="ebook",
            width=150,
            label="画質設定",
        )
        self.view_items = [
            ft.Row(
                [
                    self.label_text("PDFファイル"),
                    ft.ElevatedButton(
                        "PDFを選択",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: self.pick_file.pick_files(allow_multiple=False)
                    ),
                    self.selected_file,
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            self.directory_row(),
            self.output_name_row(),
            ft.Row(
                [
                    self.label_text("画質設定"),
                    self.quality,
                ]
            ),
            *self.execute_rows(),
        ]
        self.set_view()
        self.page.overlay.extend([self.pick_file, self.get_directory])

    def get_quality_options(self):
        return [ft.dropdown.Option(key=v, text=k) for k, v in PDF_QUALITIES.items()]

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files is not None and len(e.files) == 1:
            self.selected_file.value = e.files[0].path

        self.selected_file.update()

    def collect_errors(self):
        return self.input_file_errors(self.selected_file, "PDF") + super().collect_errors()

    def build_command(self):
        return [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-dPDFSETTINGS=/{self.quality.value}",
            f"-sOutputFile={self.output_path()}",
            self.selected_file.value,
        ]
