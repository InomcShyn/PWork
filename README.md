# 🚀 Facebook Comment Scraper - FIXED VERSION

## 📝 Mô tả
Tool scrape comment và reply từ Facebook đã được **cải thiện hoàn toàn** để fix các vấn đề:
- ❌ Chỉ lấy được 1 comment và 10 reply
- ❌ Phân biệt sai comment chính và reply
- ❌ Bỏ sót nhiều comment

## 📂 Files

### 1. `fb_comment_scraper_advanced.py` 
- Phiên bản cải thiện từ code gốc
- Thuật toán expansion và detection tốt hơn

### 2. `fb_comment_scraper_mbasic_optimized.py` ⭐ **KHUYÊN DÙNG**
- Tối ưu hoàn toàn cho mbasic.facebook.com
- Accuracy cao nhất trong việc phân biệt comment/reply
- UI đẹp hơn với progress bar

## 🔧 Cài đặt

```bash
pip3 install -r requirements.txt
```

## 🚀 Sử dụng

```bash
python3 fb_comment_scraper_mbasic_optimized.py
```

## 📋 Hướng dẫn chi tiết

### 1. **Lấy Cookie:**
- Mở Facebook trên Chrome
- F12 > Application > Cookies > facebook.com
- Copy toàn bộ cookies (hoặc ít nhất `c_user`, `xs`, `datr`)

### 2. **Nhập thông tin:**
- **Link bài viết:** Paste link Facebook post
- **Cookie:** Paste cookie đã copy
- **File xuất:** Chọn nơi lưu file Excel

### 3. **Chạy scraper:**
- Click "Bắt đầu scrape"
- Theo dõi progress bar
- Chờ hoàn thành

## ✨ Cải thiện chính

### 🎯 **Thuật toán expansion:**
- Tìm link "Xem thêm" bằng 15+ selector khác nhau
- Hỗ trợ cả tiếng Anh và tiếng Việt
- Retry mechanism thông minh
- Progressive scrolling strategy

### 🧠 **Phân biệt Comment/Reply:**
- Phân tích **indentation** (margin-left, padding-left)
- Kiểm tra **DOM nesting depth**
- **Scoring system** để quyết định chính xác
- Xử lý đặc biệt cho cấu trúc mbasic

### 🎣 **Comment detection:**
- Selector tối ưu cho mbasic Facebook
- Deduplication thông minh
- Filter UI elements hiệu quả
- Extract name/content chính xác

### 🎨 **UI improvements:**
- Progress bar thời gian thực
- Hiển thị số comment/reply riêng biệt
- Thông báo chi tiết
- Hướng dẫn sử dụng

## 📊 Kết quả mong đợi

Thay vì chỉ lấy được **1 comment + 10 reply**, bây giờ sẽ lấy được:
- ✅ **Hàng trăm comment chính**
- ✅ **Hàng nghìn reply** 
- ✅ **Phân loại chính xác** Comment vs Reply
- ✅ **Không bị lộn xộn** giữa comment và reply

## 🐛 Debug

Nếu vẫn gặp vấn đề:
1. Kiểm tra file `debug_mbasic_expanded.html` được tạo ra
2. Đảm bảo cookie còn hạn
3. Thử với bài viết public trước
4. Kiểm tra console output để xem log chi tiết

## 🎯 Tips để tăng hiệu quả

1. **Cookie tốt:** Sử dụng cookie từ account có quyền xem post
2. **Headless = False:** Để xem quá trình scrape (debug)
3. **Limit = 0:** Để lấy tất cả comment
4. **Resolve UID = True:** Để lấy được Facebook UID

---

**Phiên bản này đã được test và tối ưu hóa đặc biệt cho mbasic Facebook!** 🎉