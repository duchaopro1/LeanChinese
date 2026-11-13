# Giải tự

Web tĩnh phân tích cấu tạo chữ Hán cho người học tiếng Việt: phần âm, phần ý, bố cục, pinyin, Hán Việt, thứ tự nét, chữ cùng phần âm và từ HSK chứa chữ đó.

## Chạy thử trên máy

```bash
python3 -m http.server 8000
```

Mở http://localhost:8000. Trang cần chạy qua máy chủ web vì đọc dữ liệu bằng `fetch`.

## Bật GitHub Pages

Settings → Pages → Source: Deploy from a branch → Branch `main`, thư mục `/ (root)`. Sau vài phút trang có tại `https://<tên-tài-khoản>.github.io/<tên-repo>/`.

## Dữ liệu

`data/` được tạo bằng `tools/build.py` từ các nguồn công khai (xem `LICENSES.md`). Nghĩa tiếng Việt nằm ở `tools/vi_gloss.txt` (mỗi dòng: `chữ nghĩa`). Thêm dòng rồi chạy lại build để cập nhật `data/chars.json`.

Nguồn cần tải về một thư mục: `dictionary.txt` và `graphics.txt` (Make Me a Hanzi), `hsk.json` (complete-hsk-vocabulary), `Unihan_Readings.txt`, `hanvietData.js` (hanviet-pinyin-words), `opencc_cn2t.js` (opencc-js, `dist/esm/cn2t.js`).

```bash
python3 tools/build.py <thư-mục-nguồn> data
```
