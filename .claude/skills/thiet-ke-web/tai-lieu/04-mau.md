# Màu

Màu là thứ bậc, ý nghĩa và không khí, không phải một túi mẫu màu. Tổng hợp từ Impeccable (chiến lược, vai trò, OKLCH, tương phản) và taste-skill (tỉ lệ, bề mặt không đường kẻ, các nhóm màu bị cấm).

## 1. Số liệu từ các trang đoạt giải

- 41% trang tối, 59% sáng. Một phần tư dùng nền trắng tinh; 12% đen tuyền.
- Nút chính màu trung tính (đen, trắng, xám) trên 52% số trang. Nút có màu là một lựa chọn, không phải mặc định.
- Gradient xuất hiện ở 22% trang điểm cao và 52% trang yếu; chữ gradient 2%.
- Một trang trên 246 có nút chính màu đất nung, không trang nào có nút tím.
- Trang điểm cao đổi màu nền giữa các section thường xuyên hơn.

## 2. Chọn chiến lược trước khi chọn màu

Bốn chiến lược (Impeccable):

| Chiến lược | Mô tả | Hợp với |
|---|---|---|
| **Tiết chế** | Các màu trung tính nhuộm nhẹ từ thế giới chủ thể, cộng một màu nhấn | Thao tác, Đọc (mặc định) |
| **Cam kết** | Một màu bão hòa chiếm 30–60% bề mặt | Quảng bá, Trải nghiệm |
| **Bảng đầy đủ** | Ba, bốn màu có vai trò rõ ràng | Quảng bá khi chủ thể nhiều màu |
| **Ngập màu** | Bề mặt chính là màu | Quảng bá, chiến dịch |

Quảng bá và Trải nghiệm được phép dùng chiến lược táo bạo; chọn khi brief cho phép. **Màu cam kết ở cấp trang:** những vùng màu chiếm trọn một khu vực, không phải chấm nhấn rải rác trên nền trung tính.

**Sáng hay tối không bao giờ là mặc định.** Viết một câu về bối cảnh vật lý: ai dùng, ở đâu, dưới ánh sáng nào. Để câu đó quyết định. (Quán bar buổi tối, điện thoại trong phòng tối: tối. Thực đơn đọc lúc trưa nắng, trang hướng dẫn dùng ở văn phòng: sáng.)

## 3. Vai trò, không phải mẫu màu

Dựng màu theo vai trò:

```css
:root {
  --bg: …;         /* nền, 70–90% trang */
  --surface: …;    /* bề mặt nổi, một bậc tông so với nền */
  --ink: …;        /* chữ chính */
  --muted: …;      /* chữ phụ, vẫn đạt 4.5:1 */
  --accent: …;     /* hành động chính, focus */
  --accent-ink: …; /* chữ trên nền nhấn */
  --field-1: …; --field-1-ink: …; /* vùng màu cho section, mỗi vùng có màu chữ riêng */
  /* Thao tác thêm: --border, --success, --warning, --danger, --info, --selected */
}
```

Đổi theme thì ánh xạ lại vai trò, không đổi từng chỗ dùng.

Bảng màu mới cho web: dùng **OKLCH**, vì độ sáng và độ bão hòa chỉnh được dễ đoán. Khi tạo dải màu, thay độ sáng và **giảm độ bão hòa ở hai đầu sáng nhất và tối nhất**; đừng giữ bão hòa cao ở độ sáng cực đoan chỉ cho đều toán học. Ưu tiên màu tường minh thay vì chuỗi lớp phủ trong suốt (tương phản sẽ phụ thuộc ngữ cảnh).

Chọn sắc độ từ ý nghĩa sản phẩm và hướng thị giác, không từ liên tưởng mặc định của ngành.

## 4. Tỉ lệ (Quảng bá)

- **Nền:** 70–90% trang.
- **Mực:** chữ, và có thể một section đảo màu (mực làm nền, nền làm mực).
- **Nhấn:** dưới 5% mỗi màn hình. Đánh dấu hành động và tối đa một thứ lặp lại khác. Màu nhấn xuất hiện ở mười chỗ thì chẳng có nghĩa gì; ở đúng nút chính và một chi tiết thì nghĩa là "ở đây".
- Chữ chạy dài màu mực đầy đủ. Một trang toàn chữ xám nhạt trông chưa xong.

## 5. Bề mặt không cần đường kẻ hay bóng (Quảng bá)

- Tách bề mặt bằng **một bậc tông**. Một bậc là đủ; panel vẫn không rõ thì tăng padding hoặc tách bằng khoảng trống trước.
- Không lồng panel trong panel.
- Ảnh không cần khung. Ảnh sáng chìm vào nền sáng thì đổi khung cắt hoặc đặt ảnh lên một vùng màu.
- Một thanh dày (từ 4px) màu mực hoặc nhấn là một yếu tố đồ họa, được dùng khi hướng thiết kế có nó.

Thao tác / Đọc: đường 1px và bóng được phép khi làm rõ trạng thái, thứ bậc hoặc giúp quét thông tin (`02-man-hinh-ung-dung.md`).

## 6. Vùng màu theo chương

- Các vùng gặp nhau sát mép với một đường thẳng cứng. Không gì mờ dần sang gì.
- Mỗi vùng có màu chữ riêng trong bảng màu. Không bao giờ đặt `--muted` lên vùng có màu; lấy chữ phụ từ màu chữ của vùng đó.
- Các vùng cạnh nhau khác nhau về **độ sáng**, không chỉ sắc độ, nếu không trang sẽ rung.
- Sắp như các chương sách: mở mạnh, nghỉ, bất ngờ ở giữa, khép bằng một vùng rất tối hoặc rất sáng.
- `theme-color` của trang và thanh điều hướng theo vùng đầu tiên.

## 7. Trang tối

- `color-scheme: dark` trên `:root` để ô nhập và thanh cuộn theo.
- Nền là một tông sâu hơi nhuộm từ bảng màu; mực là một màu sáng dịu, không phải trắng tinh.
- Chữ phụ là chỗ trang tối hay hỏng: kiểm tra `--muted` so với nền đạt 4.5:1.
- Độ sâu trên nền tối đến từ một bậc bề mặt sáng hơn, không bao giờ từ ánh phát sáng hay ánh màu.
- Dùng độ đậm nhẹ hơn so với trang sáng.
- Chế độ tối của một sản phẩm được thiết kế riêng, không đảo màu máy móc.

## 8. Màu và ảnh

- Khi ảnh mang màu, giao diện giữ trung tính và lấy mực từ vùng tối nhất của ảnh.
- Không phủ màu thương hiệu lên ảnh. Hoặc để nguyên, hoặc cam kết một xử lý thật (đen trắng cả bộ, duotone cả bộ).
- Chữ trên ảnh cần một vùng yên. Không có thì đưa chữ ra khỏi ảnh. Lớp phủ tối trung tính dưới chữ là ngoại lệ duy nhất được dùng gradient.
- Một vùng màu phẳng lấy từ ảnh (bầu trời, bóng đổ của nó) khiến section ngồi cùng ảnh đó.

## 9. Tương phản

| Nội dung | WCAG AA tối thiểu |
|---|---|
| Chữ thân bài | 4.5:1 |
| Chữ lớn (từ 24px, hoặc 18.5px đậm), số hiển thị | 3:1 |
| Điều khiển, icon, vòng focus | 3:1 |

- Đo các cặp màu thật, ở mọi trạng thái: hover, disabled, lớp phủ, chữ trên ảnh, cả hai theme. Đừng chỉ tin mắt.
- Không hạ opacity chữ cho "nhẹ" mà không kiểm tra tỉ lệ kết quả.
- Focus và hover **tăng** tương phản, không bao giờ giảm.
- Thông tin truyền bằng màu cũng phải có chữ, hình, icon hoặc vị trí (người mù màu).
- Màu ngữ nghĩa nhất quán nhưng tôn trọng quy ước của nền tảng và lĩnh vực (ví dụ chứng khoán Việt Nam: tăng xanh, giảm đỏ, trần tím, sàn xanh lam).

## 10. Các nhóm màu "AI hay dùng"

Khi brief để tự do thẩm mỹ, rơi vào một trong các nhóm sau nghĩa là tự kiểm tra đã thất bại (Impeccable, taste-skill):

- **Nền kem vàng + nhấn đất nung, gỉ sét, đỏ tín hiệu,** thường đi với serif tương phản cao. Đây là "cách sửa" cho làn sóng tím trước đó, và giờ là vẻ ngoài AI dễ nhận ra nhất.
- **Tím, indigo, gradient tím sang xanh.** Làn sóng đầu tiên của trang AI là màu tím, và vẫn được đọc như vậy.
- **Gần đen với một màu neon và viền phát sáng.**
- **Báo giấy:** đường kẻ mảnh khắp nơi, serif nghiêng to, nhãn monospace nhỏ giãn chữ.
- **Màu mực phẳng bão hòa với hộp đen, bóng lệch cứng, chữ đặc hẹp nặng** (neobrutalist mặc định).

Tất cả đều hợp lệ khi brief gọi đến. Tự kiểm tra: nếu ai đó đoán được thẩm mỹ của bạn chỉ từ tên ngành, hoặc từ "tên ngành cộng danh sách điều cần tránh", làm lại cho đến khi không đoán được.

"Ấm" ở đây nghĩa là: một tông đá ít bão hòa, một màu mực sâu, một bức ảnh, hoặc một vùng màu ấm đầy đủ. Không phải kem với đất nung.

Chủ đề sách, ấm áp hay dành cho trẻ em không làm mềm quy tắc này: vải bìa sách, chỉ khâu, bìa áo sách trải khắp quang phổ bão hòa; giấy kem chỉ là góc nhỏ nhất của thế giới đó.

## 11. Thương hiệu có sẵn

Giữ màu thương hiệu đã xác nhận; gán chúng vào vai trò. Nếu thương hiệu buộc dùng màu thuộc nhóm trên (màu chủ đạo là tím), giữ nó, nói rõ trong báo cáo, và bỏ qua đúng luật đó khi soát (`--bo-qua ai-palette,ai-palette-tw`).
