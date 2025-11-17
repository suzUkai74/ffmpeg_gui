import flet as ft
import os
import subprocess
from .base_view import BaseView

class PdfCombine(BaseView):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.pick_file = ft.FilePicker(on_result=self.pick_files_result)
        self.pdf_files = []
        self.pdf_file_list = ft.Column(spacing=5)
        self.get_directry = ft.FilePicker(on_result=self.get_directry_result)
        self.selected_directry = ft.Text()
        self.directry_input_button = ft.ElevatedButton(
            "保存先ディレクトリを指定",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: self.get_directry.get_directory_path(),
        )
        self.output_file_name_input = ft.TextField(label="保存動画名", width="200")
        self.exec_button = ft.FilledButton(
            "実行",
            on_click=self.click_execute,
        )
        self.result_text = ft.Text()
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
            ft.Row(
                [
                    self.label_text("保存先ディレクトリ"),
                    self.directry_input_button,
                    self.selected_directry,
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            ft.Row(
                [
                    self.label_text("保存PDF名"),
                    self.output_file_name_input,
                ]
            ),
            ft.Row(
                [
                    self.exec_button,
                ]
            ),
            ft.Row(
                [
                    self.result_text,
                ]
            ),
        ]
        self.set_view()
        self.page.overlay.extend([self.pick_file,self.get_directry])

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.pdf_files = []
            for file in e.files:
                self.pdf_files.append(file.path)
            self.update_list()

    def get_directry_result(self, e: ft.FilePickerResultEvent):
        self.selected_directry.value = e.path if e.path else "キャンセルされました。"
        self.selected_directry.update()

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

    def validate(self):
        errors = []
        if not len(self.pdf_files) >= 2:
            errors.append("PDFを2つ以上選択してください。")

        if not self.selected_directry.value:
            errors.append("保存先ディレクトリを指定してください。")
        elif not os.path.exists(self.selected_directry.value):
            errors.append("保存先ディレクトリが存在しない。もしくは使用できない文字(/)が含まれています。")

        if not self.output_file_name_input.value:
            errors.append("保存PDF名を指定してください。")

        if errors:
            self.result_text.value = "入力項目が正しくありません。下記内容を確認してください。"
            for error in errors:
                self.result_text.value += f"\n・{error}"

            self.ref.current.update()
            return False

        return True

    def click_execute(self, e):
        self.exec_button.disabled = True
        if self.validate():
            self.result_text.value = "実行中..."
            self.ref.current.update()
            cmds = [
                "gs",
                "-sDEVICE=pdfwrite",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={self.escape_for_zsh(self.selected_directry.value)}/{self.output_file_name_input.value}.pdf",
            ]
            cmds += [self.escape_for_zsh(path) for path in self.pdf_files]
            cp = subprocess.run(' '.join(cmds), shell=True, executable='/bin/zsh', capture_output=True)
            if cp.returncode == 0:
                path = f"{self.selected_directry.value}/{self.output_file_name_input.value}.pdf"
                self.result_text.value = f"PDFが作成されました。\n{self.content_size(path)}"
            else:
                self.result_text.value = f"エラーが発生しました。\nreturncode:{cp.returncode}\nerr:{cp.stderr.decode()}"

        self.exec_button.disabled = False
        self.ref.current.update()
