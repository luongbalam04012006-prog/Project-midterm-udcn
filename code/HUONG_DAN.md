# Hướng dẫn chạy code – Topic 10 (DCC-GARCH, VaR/ES, Euler)

## 1. Cài đặt (1 lần)
pip install numpy pandas scipy matplotlib openpyxl statsmodels
(statsmodels chỉ dùng ở TV1 Phần 4; TV2–TV5 chỉ cần numpy/pandas/scipy/matplotlib – không cần thư viện `arch`.)

## 2. Cấu trúc thư mục
final/
├── code/    TV1_Data_EDA.ipynb, TV2_GARCH.ipynb, TV3_DCC.ipynb, TV4_VaR_Backtest.ipynb,
│            TV5_Euler_Stress.ipynb, project_config.py (cấu hình chung – BẮT BUỘC nằm cùng thư mục)
├── input/   FPT.xlsx, HPG.xlsx, MWG.xlsx, VCB.xlsx, VHM.xlsx
└── output/  tự sinh 5 thư mục con TV1_… → TV5_…

## 3. Thứ tự chạy (Run All từng notebook)
TV1 → TV2 → TV3 → TV4 → TV5. Mỗi notebook chỉ đọc file output của bước trước,
nên có thể chạy riêng từng notebook miễn là bước trước đã chạy ít nhất 1 lần.
TV5 có ô kiểm tra tích hợp (đủ file, khớp ngày/mã, ma trận hợp lệ) và tuỳ chọn RUN_PIPELINE = True để chạy lại cả chuỗi.

## 4. File "hợp đồng" giữa các thành viên (khai báo trong project_config.FILES)
| Từ → Đến | File | Nội dung |
|---|---|---|
| TV1 → TV2 | TV1_Data_EDA/log_returns.csv | r_t = ln(P_t/P_{t-1}) |
| TV2 → TV3 | TV2_GARCH/std_resid.csv, cond_vol.csv, garch_selected_models.csv, sigma_forecast.csv | ε, σ, μ, σ_{T+1} |
| TV3 → TV4, TV5 | TV3_DCC/dcc_matrices.npz | R_t, H_t, R_{T+1}, H_{T+1} |
| TV4 → TV5 | TV4_VaR_Backtest/var_es_timeseries.csv, backtest_results.csv | VaR/ES hằng ngày, kết quả backtest |

## 5. Muốn đổi tham số cho cả nhóm → chỉ sửa project_config.py
- Tỷ trọng: WEIGHTS (mặc định bằng nhau) hoặc điền MARKET_CAP để dùng tỷ trọng vốn hoá
- Mức tin cậy VaR: CONF_LEVELS · Cửa sổ HS: HS_WINDOW · Giai đoạn khủng hoảng: STRESS_PERIODS
- Cặp vẽ tương quan: CORR_PAIRS · Mức ý nghĩa: ALPHA
- Nếu thư mục dự án không phải D:\Năm 3\Ứng dụng công nghệ trong TCNH\final: sửa DEFAULT_BASE
