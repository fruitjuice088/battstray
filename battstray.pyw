import psutil
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw, ImageFont
import threading
import time


# Manual
DARK_THEME = True
UPDATE_RATE_SEC = 5


def create_image(percent: float, charging: bool):
    # Icon base
    ico_w, ico_h = 128, 128
    image = Image.new("RGBA", (ico_w, ico_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    text_color = "white" if DARK_THEME else "black"

    # Battery gauge (fill)
    bar_h = ico_h // 3
    bar_w = int(ico_w * (percent / 100))
    color = "lime"
    if percent < 50:
        color = "yellow"
    elif percent < 15:
        color = "red"
    if charging:
        color = "orange"
    draw.rectangle([0, ico_h - bar_h, bar_w, ico_h], fill=color)

    # Battery gauge (frame)
    frame_w = 5
    draw.rectangle([0, ico_h - bar_h, ico_w, ico_h], outline="white", width=frame_w,)

    # Battery Percentage
    text = f"{percent}"
    font_size = 86 if len(text) > 2 else 105
    font_file = "YuGothM.ttc"
    try:
        font = ImageFont.truetype(font_file, size=font_size)
    except IOError:
        print(f"Error: Font file '{font_file}' not found.")
        font = ImageFont.load_default()  # フォントがない場合はデフォルトを使用

    # Adjust text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_x = (ico_w - text_w) // 2
    text_y = -15 if len(text) <= 2 else 0
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    return image


def update_icon(icon):
    time.sleep(1)  # delay for icon.visible
    last_percent = None
    last_charging = None
    while icon.visible:
        battery = psutil.sensors_battery()
        percent = battery.percent
        charging = battery.power_plugged

        if percent != last_percent or charging != last_charging:
            icon.icon = create_image(percent, charging)
            charge_text = "Charging" if charging else "Not charging"
            icon.title = f"{charge_text}: {percent}%"

        time.sleep(UPDATE_RATE_SEC)


def quit_app(icon):
    icon.stop()


def main():
    icon = pystray.Icon("battstray")
    icon.menu = pystray.Menu(item("Exit", lambda: quit_app(icon)))

    # バッテリー残量のアイコンを設定
    battery = psutil.sensors_battery()
    icon.icon = create_image(battery.percent, battery.power_plugged)
    icon.title = f"Battery: {battery.percent}%"

    # 別スレッドでアイコンの更新を開始
    threading.Thread(target=update_icon, args=(icon,), daemon=True).start()
    icon.run()


if __name__ == "__main__":
    main()
