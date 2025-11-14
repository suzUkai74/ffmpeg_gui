# ffmpeg_gui Flet app

An example of a minimal Flet app.

To run the app:

```
source .venv/bin/activate
pip install -r requirements.txt
flet run [app_directory]
```

setup:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval $(/opt/homebrew/bin/brew shellenv)' >> .zshenv
brew install ffmpeg
brew install ghostscript
```