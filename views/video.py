import flet as ft
import cv2
import math
import os
import unicodedata
import subprocess
PREVIEW_INDEX = 12

class Video:
    def __init__(self, page: ft.Page):
        self.page = page
        self.ref = ft.Ref[ft.Column]()
        self.pick_file = ft.FilePicker(on_result=self.pick_files_result)
        self.selected_file = ft.Text()
        self.get_directry = ft.FilePicker(on_result=self.get_directry_result)
        self.selected_directry = ft.Text()
        self.exec_button = ft.FilledButton(
                          "実行",
                         on_click=self.click_execute,
                      )
        self.video_input_button = ft.ElevatedButton(
                                 "動画を選択",
                                 icon=ft.icons.UPLOAD_FILE,
                                 on_click=lambda _: self.pick_file.pick_files(),
                             )
        self.directry_input_button = ft.ElevatedButton(
                                    "保存先ディレクトリを指定",
                                    icon=ft.icons.UPLOAD_FILE,
                                    on_click=lambda _: self.get_directry.get_directory_path(),
                                )
        self.output_file_name_input = ft.TextField(label="保存動画名", width="200")
        self.crf_input_slider = ft.Slider(min=0, max=51, divisions=51, value=23, label="{value}", on_change=self.update_crf_value_text)
        self.crf_value_text = ft.Text(self.crf_input_slider.value, width="30")
        self.crf_help_text = ft.Text("※数値が小さいほど高品質になります。")
        self.aspect_text = ft.Text()
        self.definition_text = ft.Text()
        self.video_size_text = ft.Text()
        self.scale_width_input = ft.TextField(label="Width", width="80", on_change=self.scale_input_changed)
        self.scale_height_input = ft.TextField(label="Height", width="80", on_change=self.scale_input_changed)
        self.scale_help_text = ft.Text("※-1を設定するとアスペクト比を維持して自動調整します。")
        self.result_text = ft.Text()
        self.remove_audio = ft.Checkbox(value=False, on_change=self.remove_audio_changed)
        self.remove_audio_help_text = ft.Text("※音声削除と解像度は同時選択できません。")
        self.view_items = [
            ft.Row(
                [
                    self.label_text("動画"),
                    self.video_input_button,
                    self.selected_file,
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            ft.Row(
                [
                    self.label_text("動画サイズ"),
                    self.video_size_text,
                ]
            ),
            ft.Row(
                [
                    self.label_text("解像度"),
                    self.definition_text,
                ]
            ),
            ft.Row(
                [
                    self.label_text("アスペクト比"),
                    self.aspect_text,
                ]
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
                    self.label_text("保存動画名"),
                    self.output_file_name_input,
                ]
            ),
            ft.Row(
                [
                    self.label_text("品質設定"),
                    self.crf_input_slider,
                    self.crf_value_text,
                    self.crf_help_text,
                ]
            ),
            ft.Row(
                [
                    self.label_text("解像度設定"),
                    self.scale_width_input,
                    ft.Text("："),
                    self.scale_height_input,
                    self.scale_help_text,
                ]
            ),
            ft.Row(
                [
                    self.label_text("音声削除"),
                    self.remove_audio,
                    self.remove_audio_help_text,
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
        self.view = ft.Column(self.view_items, ref=self.ref)
        page.overlay.extend([self.pick_file,self.get_directry])

    def get_view(self):
        return self.view

    def remove_video_info(self):
        self.selected_file.value = ""
        self.aspect_text.value = ""
        self.definition_text.value = ""
        self.video_size_text.value = ""

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files is None:
            self.remove_video_info()
        elif len(e.files) == 1:
            self.selected_file.value = e.files[0].path
            capture = cv2.VideoCapture(self.selected_file.value)
            w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            gcd = math.gcd(w, h)
            aw = int(w / gcd)
            ah = int(h / gcd)
            self.definition_text.value = f"{w}×{h}"
            self.aspect_text.value = f"{aw}:{ah}"
            self.video_size_text.value = self.content_size(self.selected_file.value)
        else:
            self.remove_video_info()

        self.selected_file.update()
        self.aspect_text.update()
        self.definition_text.update()
        self.video_size_text.update()

    def get_directry_result(self, e: ft.FilePickerResultEvent):
        self.selected_directry.value = e.path if e.path else "キャンセルされました。"
        self.selected_directry.update()

    def update_crf_value_text(self, e):
        self.crf_value_text.value = round(self.crf_input_slider.value)
        self.crf_value_text.update()

    def load_video(self, path):
        target_video = ft.VideoMedia(path)
        if len(self.view.controls) == PREVIEW_INDEX:
            print('Removing previous video preview...')
            self.view.controls.pop()

        video = ft.Video(
                    expand=True,
                    autoplay=False,
                    aspect_ratio=1/1,
                    playlist=[target_video],
                    playlist_mode=ft.PlaylistMode.SINGLE,
                    show_controls=True,
                    filter_quality=ft.FilterQuality.NONE,
                )
        self.view.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=video,
                        alignment=ft.alignment.top_left,
                        width=300,
                        height=500,
                    )
                ]
            )
        )
        self.view.update()

    def escape_for_zsh(self, str):
        return str.replace(" ", r"\ ")

    def normalize_num(self, str):
        return unicodedata.normalize('NFKC', str)

    def validate(self):
        errors = []
        if not self.selected_file.value:
            errors.append("動画を選択してください。")
        elif not os.path.exists(self.selected_file.value):
            errors.append("動画が存在しない。もしくは使用できない文字(/)が含まれています。")

        if not self.selected_directry.value:
            errors.append("保存先ディレクトリを指定してください。")
        elif not os.path.exists(self.selected_directry.value):
            errors.append("保存先ディレクトリが存在しない。もしくは使用できない文字(/)が含まれています。")

        if not self.output_file_name_input.value:
            errors.append("保存動画名を指定してください。")

        if (self.scale_height_input.value or self.scale_width_input.value):
            self.scale_height_input.value = self.normalize_num(self.scale_height_input.value)
            self.scale_width_input.value = self.normalize_num(self.scale_width_input.value)

            if self.remove_audio.value:
                errors.append("解像度と音声削除は同時に選択できません。")
            elif (self.scale_height_input.value and not(self.scale_width_input.value)) or \
                (self.scale_width_input.value and not(self.scale_height_input.value)) or \
                (self.scale_width_input.value == "-1" and self.scale_height_input.value == "-1"):
                errors.append("解像度を正しく設定してください。")
            elif (not self.scale_height_input.value.isdecimal() and self.scale_height_input.value != "-1") or \
                (not self.scale_width_input.value.isdecimal() and self.scale_width_input.value != "-1"):
                errors.append("解像度には数値を設定してください。")

        if errors:
            self.result_text.value = "入力項目が正しくありません。下記内容を確認してください。"
            for error in errors:
                self.result_text.value += f"\n・{error}"

            self.ref.current.update()
            return False

        return True

    def content_size(self, path):
        size = os.path.getsize(path)
        if size == 0:
            return "0B"

        size = round(size / 1024 ** 2, 2)
        return f"{size}MB"
    
    def click_execute(self, e):
        self.exec_button.disabled = True
        if self.validate():
            self.result_text.value = "実行中..."
            self.ref.current.update()
            cmds = [
                "ffmpeg",
                "-y",
                "-i",
                self.escape_for_zsh(self.selected_file.value),
                "-crf",
                str(self.crf_value_text.value),
            ]
            if self.scale_width_input.value and self.scale_height_input.value:
                cmds += [
                    "-vf",
                    f"scale={self.scale_width_input.value}:{self.scale_height_input.value}",
                ]
            elif self.remove_audio.value:
                cmds += [
                    "-vcodec",
                    "copy",
                    "-an",
                ]
            
            cmds.append(f"{self.escape_for_zsh(self.selected_directry.value)}/{self.output_file_name_input.value}.mp4")
            cp = subprocess.run(' '.join(cmds), shell=True, executable='/bin/zsh', capture_output=True)
            if cp.returncode == 0:
                path = f"{self.selected_directry.value}/{self.output_file_name_input.value}.mp4"
                self.result_text.value = f"動画が作成されました。\n{self.content_size(path)}"
                self.load_video(path)
            else:
                self.result_text.value = f"エラーが発生しました。\nreturncode:{cp.returncode}\nerr:{cp.stderr.decode()}"

        self.exec_button.disabled = False
        self.ref.current.update()

    def label_text(self, text):
        return ft.Text(f"{text}：", width=150)

    def remove_audio_changed(self, e):
        self.scale_height_input.value = ""
        self.scale_width_input.value = ""
        self.scale_height_input.update()
        self.scale_width_input.update()

    def scale_input_changed(self, e):
        self.remove_audio.value = False
        self.remove_audio.update()
