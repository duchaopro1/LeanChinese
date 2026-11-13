# Giải tự

Web tĩnh cho người học tiếng Trung nói tiếng Việt, có hai chức năng:

- **Phân tích chữ Hán**: nhập một chữ, một từ hoặc một câu. Một chữ cho cấu tạo đầy đủ (phần âm, phần ý, bố cục, pinyin, Hán Việt, thứ tự nét, chữ cùng phần âm, từ HSK chứa chữ đó). Nhiều chữ cho tổng quan: tách từ, pinyin và Hán Việt từng chữ, nghĩa từng từ, thẻ cấu tạo từng chữ.
- **Dịch Việt → Trung** (`#dich`): tra từ điển offline (khoảng 600 chữ và từ HSK 1–3), dịch từng từ cho cả câu, tra ngược theo âm Hán Việt hoặc tiếng Anh. Nút "Dịch máy" tuỳ chọn gọi API MyMemory từ trình duyệt, chỉ chạy khi người dùng bấm.

## Chạy thử trên máy

```bash
python3 -m http.server 8000
```

Mở http://localhost:8000. Trang cần chạy qua máy chủ web vì đọc dữ liệu bằng `fetch`.

## Bật GitHub Pages

Settings → Pages → Source: Deploy from a branch → Branch `main`, thư mục `/ (root)`. Sau vài phút trang có tại `https://<tên-tài-khoản>.github.io/<tên-repo>/`.

## Dữ liệu

`data/` được tạo bằng `tools/build.py` từ các nguồn công khai (xem `LICENSES.md`). Nghĩa tiếng Việt nằm ở `tools/vi_gloss.txt` (chữ đơn) và `tools/vi_words.txt` (từ nhiều chữ), mỗi dòng dạng `chữ nghĩa`, các nghĩa cách nhau bằng ` · `. Thêm dòng rồi chạy lại build để cập nhật `data/` (kể cả từ điển Việt → Trung `data/lex.json`).

Nguồn cần tải về một thư mục: `dictionary.txt` và `graphics.txt` (Make Me a Hanzi), `hsk.json` (complete-hsk-vocabulary), `Unihan_Readings.txt`, `hanvietData.js` (hanviet-pinyin-words), `opencc_cn2t.js` (opencc-js, `dist/esm/cn2t.js`).

```bash
python3 tools/build.py <thư-mục-nguồn> data
```
