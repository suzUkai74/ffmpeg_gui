import flet as ft
import math
import subprocess
import unicodedata
from .command_view import CommandView

# mp4コンテナに再エンコードなしで格納できるコーデック
MP4_COPYABLE_CODECS = {"h264", "hevc", "av1", "vp9", "mpeg4"}

class Video(CommandView):
    output_name_label = "保存動画名"
    output_extension = "mp4"
    created_message = "動画が作成されました。"

    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.pick_file = ft.FilePicker(on_result=self.pick_files_result)
        self.selected_file = ft.Text()
        self.video_input_button = ft.ElevatedButton(
            "動画を選択",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: self.pick_file.pick_files(),
        )
        self.crf_input_slider = ft.Slider(min=0, max=51, divisions=51, value=23, label="{value}", on_change=self.update_crf_value_text)
        self.crf_value_text = ft.Text(self.crf_input_slider.value, width="30")
        self.crf_help_text = ft.Text("※数値が小さいほど高品質になります。")
        self.aspect_text = ft.Text()
        self.definition_text = ft.Text()
        self.video_size_text = ft.Text()
        self.scale_width_input = ft.TextField(label="Width", width="80", on_change=self.scale_input_changed)
        self.scale_height_input = ft.TextField(label="Height", width="80", on_change=self.scale_input_changed)
        self.scale_help_text = ft.Text("※-1を設定するとアスペクト比を維持して自動調整します。")
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
            self.directory_row(),
            self.output_name_row(),
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
            *self.execute_rows(),
        ]
        self.base_row_count = len(self.view_items)
        self.set_view()
        page.overlay.extend([self.pick_file, self.get_directory])

    def remove_video_info(self):
        self.selected_file.value = ""
        self.aspect_text.value = ""
        self.definition_text.value = ""
        self.video_size_text.value = ""

    def get_video_dimensions(self, path):
        try:
            cp = subprocess.run(
                [
                    self.resolve_command("ffprobe"),
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    path,
                ],
                capture_output=True,
            )
        except FileNotFoundError:
            return None

        values = cp.stdout.decode().split()
        if cp.returncode != 0 or len(values) < 2:
            return None

        w, h = int(values[0]), int(values[1])
        if w <= 0 or h <= 0:
            return None

        return w, h

    def get_video_codec(self, path):
        try:
            cp = subprocess.run(
                [
                    self.resolve_command("ffprobe"),
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=codec_name",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    path,
                ],
                capture_output=True,
            )
        except OSError:
            return None

        if cp.returncode != 0:
            return None

        return cp.stdout.decode().strip() or None

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files is not None and len(e.files) == 1:
            self.selected_file.value = e.files[0].path
            self.video_size_text.value = self.content_size(self.selected_file.value)
            dimensions = self.get_video_dimensions(self.selected_file.value)
            if dimensions:
                w, h = dimensions
                gcd = math.gcd(w, h)
                self.definition_text.value = f"{w}×{h}"
                self.aspect_text.value = f"{w // gcd}:{h // gcd}"
            else:
                self.definition_text.value = "取得できませんでした"
                self.aspect_text.value = "取得できませんでした"
        else:
            self.remove_video_info()

        self.selected_file.update()
        self.aspect_text.update()
        self.definition_text.update()
        self.video_size_text.update()

    def update_crf_value_text(self, e):
        self.crf_value_text.value = round(self.crf_input_slider.value)
        self.crf_value_text.update()

    def load_video(self, path):
        target_video = ft.VideoMedia(path)
        if len(self.view.controls) > self.base_row_count:
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

    def normalize_num(self, str):
        return unicodedata.normalize('NFKC', str)

    def collect_errors(self):
        errors = self.input_file_errors(self.selected_file, "動画")
        errors += super().collect_errors()

        if self.scale_height_input.value or self.scale_width_input.value:
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
            elif (self.scale_width_input.value.isdecimal() and int(self.scale_width_input.value) % 2 == 1) or \
                (self.scale_height_input.value.isdecimal() and int(self.scale_height_input.value) % 2 == 1):
                errors.append("解像度には偶数を設定してください。(H.264では奇数の解像度を扱えません)")

        return errors

    def build_command(self):
        cmds = [
            "ffmpeg",
            "-y",
            "-i",
            self.selected_file.value,
            "-crf",
            str(self.crf_value_text.value),
        ]
        if self.scale_width_input.value and self.scale_height_input.value:
            # -1(アスペクト比維持)は奇数になり得るため、偶数に丸める-2に変換する
            w = "-2" if self.scale_width_input.value == "-1" else self.scale_width_input.value
            h = "-2" if self.scale_height_input.value == "-1" else self.scale_height_input.value
            cmds += [
                "-vf",
                f"scale={w}:{h}",
            ]
        elif self.remove_audio.value and self.get_video_codec(self.selected_file.value) in MP4_COPYABLE_CODECS:
            cmds += [
                "-vcodec",
                "copy",
                "-an",
            ]
        else:
            # 再エンコード時、奇数解像度のソースはH.264で扱えないため偶数に切り捨てる
            cmds += [
                "-vf",
                "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            ]
            if self.remove_audio.value:
                cmds.append("-an")

        cmds.append(self.output_path())
        return cmds

    def on_success(self, path):
        self.load_video(path)

    def remove_audio_changed(self, e):
        self.scale_height_input.value = ""
        self.scale_width_input.value = ""
        self.scale_height_input.update()
        self.scale_width_input.update()

    def scale_input_changed(self, e):
        self.remove_audio.value = False
        self.remove_audio.update()
