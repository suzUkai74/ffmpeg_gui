import flet as ft
import os
import subprocess
from .base_view import BaseView

PDF_QUALITIES = {
    "低": "screen",
    "中": "ebook",
    "高": "printer",
    "最高": "prepress",
}

class PdfCompression(BaseView):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.pick_file = ft.FilePicker(on_result=self.pick_files_result)
        self.selected_file = ft.Text()
        self.get_directry = ft.FilePicker(on_result=self.get_directry_result)
        self.selected_directry = ft.Text()
        self.directry_input_button = ft.ElevatedButton(
            "保存先ディレクトリを指定",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: self.get_directry.get_directory_path(),
        )
        self.output_file_name_input = ft.TextField(label="保存動画名", width="200")
        self.quality = ft.Dropdown(
            options=self.get_quality_options(),
            value="ebook",
            width=150,
            label="画質設定",
        )
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
                        on_click=lambda _: self.pick_file.pick_files(allow_multiple=False)
                    ),
                    self.selected_file,
                ],
                scroll=ft.ScrollMode.AUTO
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
                    self.label_text("画質設定"),
                    self.quality,
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
    
    def get_quality_options(self):
        return [ft.dropdown.Option(key=v, text=k) for k, v in PDF_QUALITIES.items()]

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if len(e.files) == 1:
            self.selected_file.value = e.files[0].path

        self.selected_file.update()

    def get_directry_result(self, e: ft.FilePickerResultEvent):
        self.selected_directry.value = e.path if e.path else "キャンセルされました。"
        self.selected_directry.update()

    def validate(self):
        errors = []
        if not self.selected_file.value:
            errors.append("PDFを選択してください。")
        elif not os.path.exists(self.selected_file.value):
            errors.append("PDFが存在しない。もしくは使用できない文字(/)が含まれています。")

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
                "-dCompatibilityLevel=1.4",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-dPDFSETTINGS=/{self.quality.value}",
                f"-sOutputFile={self.escape_for_zsh(self.selected_directry.value)}/{self.output_file_name_input.value}.pdf",
                f"{self.escape_for_zsh(self.selected_file.value)}",
            ]
            cp = subprocess.run(' '.join(cmds), shell=True, executable='/bin/zsh', capture_output=True)
            if cp.returncode == 0:
                path = f"{self.selected_directry.value}/{self.output_file_name_input.value}.pdf"
                self.result_text.value = f"PDFが作成されました。\n{self.content_size(path)}"
            else:
                self.result_text.value = f"エラーが発生しました。\nreturncode:{cp.returncode}\nerr:{cp.stderr.decode()}"

        self.exec_button.disabled = False
        self.ref.current.update()
