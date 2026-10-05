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


def print_menu():
    print("\n=== TẢI ẢNH THIÊN NHIÊN ===")
    for key, (name, _) in THEMES.items():
        print(f"{key}. {name}")
    print("0. Thoát")


def safe_name(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:60] or "image"


def fetch_unsplash_images(query: str, count: int):
    if not UNSPLASH_ACCESS_KEY:
        raise RuntimeError(
            "Chưa có API key Unsplash. Hãy chạy:\n"
            "export UNSPLASH_ACCESS_KEY='your_key_here'\n"
            "hoặc set biến môi trường trong Windows."
        )

    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {
        "query": query,
        "per_page": min(count, 30),
        "page": 1,
        "orientation": "landscape",
    }

    response = requests.get(UNSPLASH_API, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    if not results:
        raise RuntimeError(f"Không tìm thấy ảnh cho từ khóa: {query}")

    urls = []
    for item in results[:count]:
        url = item.get("urls", {}).get("regular")
        if url:
            urls.append(url)
    return urls


def download_file(url: str, folder: Path, filename: str):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    file_path = folder / filename
    file_path.write_bytes(response.content)
    return file_path


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
    
    while True:
        print_menu()
        choice = input("\nChọn chủ đề: ").strip()

        if choice == "0":
            print("Tạm biệt!")
            break

        if choice not in THEMES:
            print("Lựa chọn không hợp lệ. Vui lòng chọn 1, 2, 3, 4 hoặc 0.")
            continue

        topic_name, query = THEMES[choice]
        try:
            amount = int(input(f"Số lượng ảnh muốn tải cho '{topic_name}': ").strip())
        except ValueError:
            print("Số lượng phải là số nguyên.")
            continue

        if amount <= 0:
            print("Số lượng phải lớn hơn 0.")
            continue

        folder = Path("downloads") / safe_name(topic_name)
        folder.mkdir(parents=True, exist_ok=True)

        print(f"\nĐang tìm ảnh cho: {topic_name} ...")
        try:
            image_urls = fetch_unsplash_images(query, amount)
        except Exception as e:
            print(f"Lỗi khi tìm ảnh: {e}")
            continue

        downloaded = 0
        for idx, url in enumerate(image_urls, start=1):
            try:
                filename = f"{safe_name(topic_name)}_{idx}.jpg"
                save_path = download_file(url, folder, filename)
                print(f"[OK] {idx}/{len(image_urls)} -> {save_path}")
                downloaded += 1
                time.sleep(0.5)
            except Exception as e:
                print(f"[FAIL] Không tải được ảnh thứ {idx}: {e}")

        print(f"\nHoàn tất. Đã tải {downloaded}/{amount} ảnh vào: {folder.resolve()}")
        again = input("\nBạn muốn tải tiếp? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("Kết thúc.")
            break


if __name__ == "__main__":
    main()
