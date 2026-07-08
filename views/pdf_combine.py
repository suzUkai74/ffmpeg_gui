import flet as ft
from .command_view import CommandView

class PdfCombine(CommandView):
    output_name_label = "保存PDF名"
    output_extension = "pdf"
    created_message = "PDFが作成されました。"

    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.pick_file = ft.FilePicker(on_result=self.pick_files_result)
        self.pdf_files = []
        self.pdf_file_list = ft.Column(spacing=5)
        self.view_items = [
            ft.Row(
                [
                    self.label_text("PDFファイル"),
                    ft.ElevatedButton(
                        "PDFを選択",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: self.pick_file.pick_files(allow_multiple=True),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            ft.Row(
                [
                    self.label_text("PDFファイル順序"),
                    self.pdf_file_list,
                ],
            ),
            self.directory_row(),
            self.output_name_row(),
            *self.execute_rows(),
        ]
        self.set_view()
        self.page.overlay.extend([self.pick_file, self.get_directory])

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.pdf_files = [file.path for file in e.files]
            self.update_list()

    def move_up(self, e, index):
        if index > 0:
            self.pdf_files[index - 1], self.pdf_files[index] = self.pdf_files[index], self.pdf_files[index - 1]
            self.update_list()

    def move_down(self, e, index):
        if index < len(self.pdf_files) - 1:
            self.pdf_files[index + 1], self.pdf_files[index] = self.pdf_files[index], self.pdf_files[index + 1]
            self.update_list()

    def update_list(self):
        self.pdf_file_list.controls.clear()
        for i, filepath in enumerate(self.pdf_files):
            row = ft.Row(
                [
                    ft.Text(self.get_filename(filepath), width=150),
                    ft.IconButton(ft.icons.ARROW_UPWARD, on_click=lambda e, i=i: self.move_up(e, i)),
                    ft.IconButton(ft.icons.ARROW_DOWNWARD, on_click=lambda e, i=i: self.move_down(e, i)),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
            self.pdf_file_list.controls.append(row)
        self.ref.current.update()

    def collect_errors(self):
        errors = []
        if len(self.pdf_files) < 2:
            errors.append("PDFを2つ以上選択してください。")

        return errors + super().collect_errors()

    def build_command(self):
        return [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={self.output_path()}",
            *self.pdf_files,
        ]
