import flet as ft
import os
import shutil
import subprocess
from .base_view import BaseView

# Finder起動時はPATHにHomebrew等が含まれないため、明示的に探索する
COMMAND_SEARCH_DIRS = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
]

class CommandView(BaseView):
    """外部コマンドを実行してファイルを出力するビューの共通処理。

    サブクラスは output_name_label / output_extension / created_message を
    定義し、build_command() でコマンドをリスト形式で返す。
    """

    output_name_label = "保存ファイル名"
    output_extension = ""
    created_message = "ファイルが作成されました。"

    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.get_directory = ft.FilePicker(on_result=self.get_directory_result)
        self.selected_directory = ft.Text()
        self.directory_input_button = ft.ElevatedButton(
            "保存先ディレクトリを指定",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: self.get_directory.get_directory_path(),
        )
        self.output_file_name_input = ft.TextField(label=self.output_name_label, width="200")
        self.allow_overwrite = ft.Checkbox(label="上書きを許可", value=False)
        self.exec_button = ft.FilledButton(
            "実行",
            on_click=self.click_execute,
        )
        self.result_text = ft.Text()

    def directory_row(self):
        return ft.Row(
            [
                self.label_text("保存先ディレクトリ"),
                self.directory_input_button,
                self.selected_directory,
            ],
            scroll=ft.ScrollMode.AUTO
        )

    def output_name_row(self):
        return ft.Row(
            [
                self.label_text(self.output_name_label),
                self.output_file_name_input,
                self.allow_overwrite,
            ]
        )

    def execute_rows(self):
        return [
            ft.Row([self.exec_button]),
            ft.Row([self.result_text]),
        ]

    def get_directory_result(self, e: ft.FilePickerResultEvent):
        self.selected_directory.value = e.path if e.path else "キャンセルされました。"
        self.selected_directory.update()

    def resolve_command(self, name):
        found = shutil.which(name)
        if found:
            return found

        for directory in COMMAND_SEARCH_DIRS:
            candidate = os.path.join(directory, name)
            if os.access(candidate, os.X_OK):
                return candidate

        return name

    def output_path(self):
        return f"{self.selected_directory.value}/{self.output_file_name_input.value}.{self.output_extension}"

    def input_file_errors(self, selected_file, label):
        errors = []
        if not selected_file.value:
            errors.append(f"{label}を選択してください。")
        elif not os.path.exists(selected_file.value):
            errors.append(f"{label}が存在しない。もしくは使用できない文字(/)が含まれています。")
        return errors

    def collect_errors(self):
        errors = []
        directory_ok = False
        if not self.selected_directory.value:
            errors.append("保存先ディレクトリを指定してください。")
        elif not os.path.exists(self.selected_directory.value):
            errors.append("保存先ディレクトリが存在しない。もしくは使用できない文字(/)が含まれています。")
        else:
            directory_ok = True

        name_ok = False
        if not self.output_file_name_input.value:
            errors.append(f"{self.output_name_label}を指定してください。")
        elif "/" in self.output_file_name_input.value:
            errors.append(f"{self.output_name_label}に使用できない文字(/)が含まれています。")
        else:
            name_ok = True

        if directory_ok and name_ok and not self.allow_overwrite.value and os.path.exists(self.output_path()):
            errors.append("同名のファイルが既に存在します。上書きする場合は「上書きを許可」をチェックしてください。")

        return errors

    def validate(self):
        errors = self.collect_errors()
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
            cmds = self.build_command()
            cmds[0] = self.resolve_command(cmds[0])
            try:
                cp = subprocess.run(cmds, capture_output=True)
            except FileNotFoundError:
                self.result_text.value = f"コマンド({cmds[0]})が見つかりません。インストールされているか確認してください。"
            else:
                if cp.returncode == 0:
                    path = self.output_path()
                    self.result_text.value = f"{self.created_message}\n{self.content_size(path)}"
                    self.on_success(path)
                else:
                    self.result_text.value = f"エラーが発生しました。\nreturncode:{cp.returncode}\nerr:{cp.stderr.decode()}"

        self.exec_button.disabled = False
        self.ref.current.update()

    def build_command(self):
        raise NotImplementedError

    def on_success(self, path):
        pass
