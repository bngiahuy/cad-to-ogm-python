# CAD to OGM Python Module

Chuyển đổi ảnh CAD (PNG) thành lưới occupancy (OGM) 2D dạng numpy array.

## 1. Mục đích
- Tự động chuyển bản vẽ CAD (dạng ảnh PNG) thành ma trận occupancy grid (OGM) nhị phân, phục vụ các bài toán robot, mô phỏng, AI, v.v.
- Có thể sử dụng như script độc lập (`main.py`) hoặc import như module tái sử dụng (`cad_ogm.py`).

## 2. Cài đặt
- Python >= 3.10
- Cài các thư viện cần thiết:

```bash
pip install numpy opencv-python matplotlib
```

## 3. Sử dụng nhanh với main.py
- Chạy trực tiếp để test pipeline:

```bash
python main.py
```
- Sửa đường dẫn ảnh đầu vào trong `main.py` nếu cần.
- Kết quả: In ra OGM, hiển thị ảnh, lưu file numpy và csv trong thư mục `output/`.

## 4. Sử dụng như module (import cad_ogm.py)
- Import hàm chính trong project khác:

```python
from cad_ogm import cad_to_ogm
ogm = cad_to_ogm(
    'mycad.png',
    grid_size=(300, 300),
    fill_closed_regions_flag=False,
)
```
- Hàm trả về numpy 2D array (0: free, 1: obstacle).
- Có thể điều chỉnh các tham số:
    - `grid_size`: Kích thước lưới đầu ra (mặc định 400x400)
    - `fill_closed_regions_flag`: Lấp kín các vùng trống khép kín (True/False, mặc định False)

## 5. Input/Output
- **Input:** Đường dẫn ảnh PNG bản vẽ CAD (nên là ảnh trắng đen, tường tối, nền sáng). Ảnh nên có nền trắng (255), tường đen (0), có thể có watermark xám (~230-240). `(lưu ý: không hỗ trợ ảnh SVG)`
- **Output:**
    - numpy 2D array nhị phân (0: free space, 1: obstacle/wall)

## 6. Logic xử lý ảnh
Pipeline xử lý bao gồm các bước sau:
1. **Tải ảnh:** Đọc ảnh grayscale từ đường dẫn.
2. **Tiền xử lý:** 
   - Ngưỡng hóa (threshold) để chuyển thành ảnh nhị phân (tường đen trên nền trắng).
   - Loại bỏ nhiễu nhỏ bằng cách lọc các thành phần liên thông dưới ngưỡng kích thước.
   - Mở rộng (dilate) đường kẻ để đảm bảo tường dày đủ sau khi thu nhỏ.
3. **Chuyển thành lưới:** Thu nhỏ ảnh về kích thước lưới mong muốn bằng interpolation INTER_AREA để giữ nguyên đường kẻ, sau đó nhị phân hóa lại.
4. **Lấp kín vùng khép kín (tùy chọn):** Sử dụng flood fill để lấp kín các vùng trống không kết nối với biên ngoài.

Lưu ý: Logic được thiết kế cho ảnh CAD có đường kẻ mỏng, cần mở rộng để tránh mất đường khi thu nhỏ.

## 7. Tuỳ biến
- Có thể chỉnh sửa các hàm trong `cad_ogm.py` để phù hợp pipeline riêng.
- Nếu muốn xuất ảnh, CSV, hoặc visualize, hãy tự xử lý với numpy/matplotlib.
