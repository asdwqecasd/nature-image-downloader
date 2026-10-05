import re
import time
from pathlib import Path

import requests


THEMES = {
    "1": ("Biển cả", "sea ocean coast landscape"),
    "2": ("Rừng già", "tropical rainforest jungle landscape"),
    "3": ("Mùa đông tuyết trắng", "winter snow mountain landscape"),
    "4": ("Thiên nhiên kiểu anime", "anime nature landscape"),
}

PIXABAY_API = "https://pixabay.com/api/"
PIXABAY_KEY = "46802026-ca31a35e96b436798e64dc00d"
MAX_IMAGES = 9999
TARGET_FOLDER = Path("downloads") / "anh thien nhien"


def print_menu():
    print("\n=== TẢI ẢNH THIÊN NHIÊN ===")
    for key, (name, _) in THEMES.items():
        print(f"{key}. {name}")
    print("5. Tải tất cả chủ đề vào cùng một thư mục")
    print("0. Thoát")


def safe_name(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:60] or "image"


def create_downloads_dir():
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục lưu ảnh: {TARGET_FOLDER.resolve()}")


def fetch_pixabay_images(query: str, count: int):
    urls = []
    params = {
        "key": PIXABAY_KEY,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "per_page": min(count, 200),
        "page": 1,
    }

    try:
        response = requests.get(PIXABAY_API, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", [])

        if not hits:
            print(f"Pixabay: Không tìm thấy ảnh cho '{query}'")
            return urls

        for item in hits[:count]:
            url = item.get("largeImageURL") or item.get("webformatURL")
            if url:
                urls.append(url)

        print(f"Pixabay: Tìm được {len(urls)}/{count} ảnh cho '{query}'")
    except Exception as e:
        print(f"Lỗi Pixabay: {e}")

    return urls


def download_file(url: str, folder: Path, filename: str):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        file_path = folder / filename
        file_path.write_bytes(response.content)
        return True
    except Exception as e:
        print(f"Lỗi tải file: {e}")
        return False


def download_theme_images(topic_name: str, query: str, amount: int):
    folder = TARGET_FOLDER
    folder.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"Đang tìm ảnh cho: {topic_name}")
    print(f"{'=' * 60}")

    image_urls = fetch_pixabay_images(query, amount)
    if not image_urls:
        print(f"⚠ Không tìm được ảnh cho '{topic_name}'")
        return 0

    print(f"\nBắt đầu tải {len(image_urls)} ảnh cho '{topic_name}' vào {folder.resolve()}...")
    downloaded = 0
    for idx, url in enumerate(image_urls, start=1):
        filename = f"{safe_name(topic_name)}_{idx:04d}.jpg"
        if download_file(url, folder, filename):
            print(f"[OK] {idx}/{len(image_urls)} -> {filename}")
            downloaded += 1
            time.sleep(0.2)
        else:
            print(f"[FAIL] Không tải được ảnh thứ {idx}")

    print(f"\n✓ Hoàn tất: Đã tải {downloaded}/{amount} ảnh cho '{topic_name}'")
    return downloaded


def main():
    create_downloads_dir()
    print(f"✓ Tối đa có thể tải: {MAX_IMAGES} ảnh\n")

    while True:
        print_menu()
        choice = input("\nChọn chủ đề: ").strip()

        if choice == "0":
            print("Tạm biệt!")
            break

        if choice == "5":
            try:
                total_amount = int(input(f"Tổng số lượng ảnh cho tất cả chủ đề (tối đa {MAX_IMAGES}): ").strip())
            except ValueError:
                print("Số lượng phải là số nguyên.")
                continue

            if total_amount <= 0:
                print("Số lượng phải lớn hơn 0.")
                continue

            if total_amount > MAX_IMAGES:
                print(f"Số lượng vượt quá tối đa {MAX_IMAGES}. Sẽ tải {MAX_IMAGES} ảnh.")
                total_amount = MAX_IMAGES

            num_themes = len(THEMES)
            per_theme = total_amount // num_themes
            remainder = total_amount % num_themes

            total_downloaded = 0
            for idx, (key, (topic_name, query)) in enumerate(THEMES.items()):
                amount = per_theme + (remainder if idx == num_themes - 1 else 0)
                total_downloaded += download_theme_images(topic_name, query, amount)

            print(f"\n{'=' * 60}")
            print(f"✅ TỔNG CỘNG: Đã tải {total_downloaded}/{total_amount} ảnh vào thư mục")
            print(f"  {TARGET_FOLDER.resolve()}")
            print(f"{'=' * 60}")

            again = input("\nBạn muốn tải tiếp? (y/n): ").strip().lower()
            if again not in ("y", "yes"):
                print("Kết thúc.")
                break
            continue

        if choice not in THEMES:
            print("Lựa chọn không hợp lệ. Vui lòng chọn 1, 2, 3, 4, 5 hoặc 0.")
            continue

        topic_name, query = THEMES[choice]
        try:
            amount = int(input(f"Số lượng ảnh muốn tải cho '{topic_name}' (tối đa {MAX_IMAGES}): ").strip())
        except ValueError:
            print("Số lượng phải là số nguyên.")
            continue

        if amount <= 0:
            print("Số lượng phải lớn hơn 0.")
            continue

        if amount > MAX_IMAGES:
            print(f"Số lượng vượt quá tối đa {MAX_IMAGES}. Sẽ tải {MAX_IMAGES} ảnh.")
            amount = MAX_IMAGES

        download_theme_images(topic_name, query, amount)

        again = input("\nBạn muốn tải tiếp? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("Kết thúc.")
            break


if __name__ == "__main__":
    main()
