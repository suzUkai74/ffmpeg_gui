import flet as ft
import subprocess
import os

def main(page: ft.Page):
    page.title = "ffmpeg GUI"
    page.scroll = ft.ScrollMode.AUTO
    PREVIEW_INDEX = 8

    def pick_files_result(e: ft.FilePickerResultEvent):
        if len(e.files) == 1:
            selected_file.value = e.files[0].path
        else:
            selected_file.value = ""

        selected_file.update()

    def get_directry_result(e: ft.FilePickerResultEvent):
        selected_directry.value = e.path if e.path else "キャンセルされました。"
        selected_directry.update()

    def update_crf_value_text(e):
        crf_value_text.value = round(crf_input_slider.value)
        crf_value_text.update()

    def load_video(path):
        target_video = ft.VideoMedia(path)
        if len(page.controls) == PREVIEW_INDEX:
            page.controls.pop()

        video = ft.Video(
                    expand=True,
                    autoplay=False,
                    aspect_ratio=1/1,
                    playlist=[target_video],
                    playlist_mode=ft.PlaylistMode.SINGLE,
                    show_controls=True,
                    filter_quality=ft.FilterQuality.NONE,
                )
        page.add(
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
        page.update()

    def escape_for_zsh(str):
        return str.replace(" ", r"\ ")

    def validate():
        errors = []
        if not selected_file.value:
            errors.append("動画を選択してください。")

        if not selected_directry.value:
            errors.append("保存先ディレクトリを指定してください。")

        if not output_file_name_input.value:
            errors.append("保存動画名を指定してください。")

        if (scale_height_input.value and not(scale_width_input.value)) or \
            scale_width_input.value and not(scale_height_input.value) or \
            scale_width_input.value == "-1" and scale_height_input.value == "-1":
            errors.append("scaleを正しく設定してください。")

        if errors:
            result_text.value = "入力項目に不足があります。"
            for error in errors:
                result_text.value += f"\n{error}"

            page.update()
            return False

        return True

    def content_size(path):
        size = os.path.getsize(path)
        if size == 0:
            return "0B"

        size = round(size / 1024 ** 2, 2)
        return f"{size}MB"
    
    def click_execute(e):
        exec_button.disabled = True
        if validate():
            result_text.value = "実行中..."
            page.update()
            cmds = [
                "ffmpeg",
                "-y",
                "-i",
                escape_for_zsh(selected_file.value),
                "-crf",
                str(crf_value_text.value),
            ]
            if scale_width_input.value and scale_height_input.value:
                cmds += [
                    "-vf",
                    f"scale={scale_width_input.value}:{scale_height_input.value}",
                ]
            
            cmds.append(f"{escape_for_zsh(selected_directry.value)}/{output_file_name_input.value}.mp4")
            cp = subprocess.run(' '.join(cmds), shell=True, executable='/bin/zsh', capture_output=True)
            if cp.returncode == 0:
                path = f"{selected_directry.value}/{output_file_name_input.value}.mp4"
                result_text.value = f"動画が作成されました。\n{content_size(path)}"
                load_video(path)
            else:
                result_text.value = f"エラーが発生しました。\nreturncode:{cp.returncode}\nerr:{cp.stderr.decode()}"

        exec_button.disabled = False
        page.update()
        return

    def label_text(text):
        return ft.Text(f"{text}：", width=150)
    
    pick_file = ft.FilePicker(on_result=pick_files_result)
    selected_file = ft.Text()
    get_directry = ft.FilePicker(on_result=get_directry_result)
    selected_directry = ft.Text()
    exec_button = ft.FilledButton(
                      "実行",
                     on_click=click_execute,
                  )
    video_input_button = ft.ElevatedButton(
                             "動画を選択",
                             icon=ft.icons.UPLOAD_FILE,
                             on_click=lambda _: pick_file.pick_files(),
                         )
    directry_input_button = ft.ElevatedButton(
                                "保存先ディレクトリを指定",
                                icon=ft.icons.UPLOAD_FILE,
                                on_click=lambda _: get_directry.get_directory_path(),
                            )
    output_file_name_input = ft.TextField(label="保存動画名", width="200")
    crf_input_slider = ft.Slider(min=0, max=51, divisions=51, value=23, label="{value}", on_change=update_crf_value_text)
    crf_value_text = ft.Text(crf_input_slider.value, width="30")
    crf_help_text = ft.Text("※数値が小さいほど高品質になります。")
    scale_width_input = ft.TextField(label="Width", width="80")
    scale_height_input = ft.TextField(label="Height", width="80")
    scale_help_text = ft.Text("※-1を設定するとアスペクト比を維持して自動調整します。")
    result_text = ft.Text()
    page.overlay.extend([pick_file,get_directry])

    page.add(
        ft.Row(
            [
                label_text("動画"),
                video_input_button,
                selected_file,
            ]
        ),
        ft.Row(
            [
                label_text("保存先ディレクトリ"),
                directry_input_button,
                selected_directry,
            ]
        ),
        ft.Row(
            [
                label_text("保存動画名"),
                output_file_name_input,
            ]
        ),
        ft.Row(
            [
                label_text("crf"),
                crf_input_slider,
                crf_value_text,
                crf_help_text,
            ]
        ),
        ft.Row(
            [
                label_text("scale"),
                scale_width_input,
                ft.Text("："),
                scale_height_input,
                scale_help_text,
            ]
        ),
        ft.Row(
            [
                exec_button,
            ]
        ),
        ft.Row(
            [
                result_text,
            ]
        ),
    )

ft.app(main)
