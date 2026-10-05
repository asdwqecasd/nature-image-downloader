import os
import re
import sys
import time
from pathlib import Path

import requests


THEMES = {
    "1": ("Biển cả", "sea ocean coast landscape"),
    "2": ("Rừng già", "tropical rainforest jungle landscape"),
    "3": ("Mùa đông tuyết trắng", "winter snow mountain landscape"),
    "4": ("Thiên nhiên kiểu anime", "anime nature landscape"),
}

UNSPLASH_API = "https://api.unsplash.com/search/photos"
# API Key của bạn đã được nhúng sẵn
UNSPLASH_ACCESS_KEY = "5j-Fcs1cdGIApLE50oSO0YWz-yeIImx5zmNZcxMYPx0"
MAX_IMAGES = 9999


def print_menu():
    print("\n=== TẢI ẢNH THIÊN NHIÊN ===")
    for key, (name, _) in THEMES.items():
        print(f"{key}. {name}")
    print("5. Tải tất cả chủ đề")
    print("0. Thoát")


def safe_name(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:60] or "image"


def fetch_unsplash_images(query: str, count: int):
    """Lấy URL ảnh từ Unsplash API với hỗ trợ phân trang"""
    if not UNSPLASH_ACCESS_KEY:
        raise RuntimeError(
            "Chưa có API key Unsplash. Hãy chạy:\n"
            "export UNSPLASH_ACCESS_KEY='your_key_here'\n"
            "hoặc set biến môi trường trong Windows."
        )

    urls = []
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    per_page = 30
    total_pages = (count + per_page - 1) // per_page

    print(f"Đang tải từ {total_pages} trang (30 ảnh/trang)...")

    for page in range(1, total_pages + 1):
        params = {
            "query": query,
            "per_page": per_page,
            "page": page,
            "orientation": "landscape",
        }

        try:
            response = requests.get(UNSPLASH_API, headers=headers, params=params, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"[FAIL] Lỗi khi tải trang {page}: {e}")
            break

        data = response.json()
        results = data.get("results", [])

        if not results:
            print(f"Trang {page}: Không tìm thấy ảnh nữa")
            break

        for item in results:
            if len(urls) >= count:
                break
            url = item.get("urls", {}).get("regular")
            if url:
                urls.append(url)

        print(f"Trang {page}: Đã lấy {len(urls)}/{count} ảnh")
        time.sleep(0.3)

        if len(urls) >= count:
            break

    if not urls:
        raise RuntimeError(f"Không tìm thấy ảnh cho từ khóa: {query}")

    return urls[:count]


def download_theme_images(topic_name: str, query: str, amount: int):
    folder = Path("downloads") / safe_name(topic_name)
    folder.mkdir(parents=True, exist_ok=True)

    print(f"\nĐang tìm ảnh cho: {topic_name} ...")
    try:
        image_urls = fetch_unsplash_images(query, amount)
    except Exception as e:
        print(f"Lỗi khi tìm ảnh cho '{topic_name}': {e}")
        return 0

    print(f"\nBắt đầu tải {len(image_urls)} ảnh cho '{topic_name}'...")
    downloaded = 0
    for idx, url in enumerate(image_urls, start=1):
        try:
            filename = f"{safe_name(topic_name)}_{idx:04d}.jpg"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            file_path = folder / filename
            file_path.write_bytes(response.content)
            print(f"[OK] {idx}/{len(image_urls)} -> {filename}")
            downloaded += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"[FAIL] Không tải được ảnh thứ {idx}: {e}")

    print(f"\n✓ Hoàn tất. Đã tải {downloaded}/{amount} ảnh cho '{topic_name}' vào:")
    print(f"  {folder.resolve()}")
    return downloaded


def main():
    if not UNSPLASH_ACCESS_KEY:
        print("Lưu ý: bạn cần api key Unsplash.")
        print("Cách dùng:")
        print("  Linux/macOS: export UNSPLASH_ACCESS_KEY='KEY_CUA_BAN'")
        print("  Windows: set UNSPLASH_ACCESS_KEY=KEY_CUA_BAN")
        print("\nBạn có thể lấy key miễn phí tại: https://unsplash.com/developers")
        input("\nNhấn Enter để thoát...")
        return

    print(f"✓ API Key được tải thành công!")
    print(f"✓ Tối đa có thể tải: {MAX_IMAGES} ảnh mỗi chủ đề\n")

    while True:
        print_menu()
        choice = input("\nChọn chủ đề: ").strip()

        if choice == "0":
            print("Tạm biệt!")
            break

        if choice == "5":
            try:
                amount = int(input(f"Số lượng ảnh cho mỗi chủ đề (tối đa {MAX_IMAGES}): ").strip())
            except ValueError:
                print("Số lượng phải là số nguyên.")
                continue

            if amount <= 0:
                print("Số lượng phải lớn hơn 0.")
                continue

            if amount > MAX_IMAGES:
                print(f"Số lượng vượt quá tối đa {MAX_IMAGES}. Sẽ tải {MAX_IMAGES} ảnh cho mỗi chủ đề.")
                amount = MAX_IMAGES

            total_downloaded = 0
            for topic_name, query in THEMES.values():
                total_downloaded += download_theme_images(topic_name, query, amount)

            print(f"\n✅ Tổng số ảnh đã tải từ tất cả chủ đề: {total_downloaded}")
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
