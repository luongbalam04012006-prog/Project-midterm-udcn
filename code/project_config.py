# -*- coding: utf-8 -*-
"""
project_config.py – CẤU HÌNH CHUNG CHO CẢ 5 THÀNH VIÊN
=====================================================
Mọi notebook trong thư mục code/ đều chạy dòng:  from project_config import *
=> dùng CHUNG một bộ đường dẫn, hằng số, tỷ trọng danh mục và giai đoạn khủng hoảng.
Muốn đổi tham số cho cả nhóm (mức ý nghĩa, tỷ trọng, cửa sổ HS...) thì chỉ sửa Ở ĐÂY.

Cấu trúc thư mục:
    final/
    ├── code/     <- các notebook TV1..TV5 + file này
    ├── input/    <- 5 file .xlsx giá thô (FPT.xlsx, HPG.xlsx, ...)
    └── output/
        ├── TV1_Data_EDA/        (TV1 ghi)  -> TV2 đọc log_returns.csv
        ├── TV2_GARCH/           (TV2 ghi)  -> TV3 đọc std_resid.csv, cond_vol.csv
        ├── TV3_DCC/             (TV3 ghi)  -> TV4, TV5 đọc dcc_matrices.npz
        ├── TV4_VaR_Backtest/    (TV4 ghi)  -> TV5 đọc var_es_timeseries.csv
        └── TV5_Euler_Stress/    (TV5 ghi)

Luồng dữ liệu (mỗi bước CHỈ đọc file của bước trước, không dùng biến trong bộ nhớ):
    input/*.xlsx --TV1--> giá sạch, log return r_t
                 --TV2--> mu_i, sigma_{i,t}, phần dư chuẩn hoá eps_{i,t}
                 --TV3--> R_t, H_t = D_t R_t D_t
                 --TV4--> sigma_p,t = sqrt(w' H_t w), VaR, ES, backtest
                 --TV5--> Euler RC_i, stress periods, khuyến nghị
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


# ============================================================================
# 1. ĐƯỜNG DẪN
# ============================================================================
DEFAULT_BASE = Path(r"D:\Năm 3\Ứng dụng công nghệ trong TCNH\final")


def find_base_dir() -> Path:
    """Ưu tiên: biến môi trường PROJECT_DIR -> đường dẫn mặc định -> thư mục cha của code/."""
    env = os.environ.get("PROJECT_DIR")
    if env:
        return Path(env)
    if DEFAULT_BASE.exists():
        return DEFAULT_BASE
    here = Path.cwd()
    return here.parent if here.name.lower() == "code" else here


def _subdir(base: Path, name: str) -> Path:
    """Tìm thư mục con không phân biệt hoa/thường (input/Input/INPUT đều được)."""
    if base.exists():
        for p in base.iterdir():
            if p.is_dir() and p.name.lower() == name.lower():
                return p
    return base / name


BASE_DIR = find_base_dir()
INPUT_DIR = _subdir(BASE_DIR, "input")
OUTPUT_DIR = _subdir(BASE_DIR, "output")

TV1_DIR = OUTPUT_DIR / "TV1_Data_EDA"
TV2_DIR = OUTPUT_DIR / "TV2_GARCH"
TV3_DIR = OUTPUT_DIR / "TV3_DCC"
TV4_DIR = OUTPUT_DIR / "TV4_VaR_Backtest"
TV5_DIR = OUTPUT_DIR / "TV5_Euler_Stress"
for _d in (OUTPUT_DIR, TV1_DIR, TV2_DIR, TV3_DIR, TV4_DIR, TV5_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Tên file "hợp đồng" giữa các thành viên – KHÔNG đổi tên tuỳ tiện
FILES = {
    # TV1 -> TV2..TV5
    "prices":        TV1_DIR / "panel_AdjClose.csv",      # giá Adj Close đã căn lịch
    "log_returns":   TV1_DIR / "log_returns.csv",         # r_t = ln(P_t/P_{t-1})  (ĐẦU VÀO CHÍNH THỨC)
    # TV2 -> TV3..TV5
    "garch_selected": TV2_DIR / "garch_selected_models.csv",
    "std_resid":     TV2_DIR / "std_resid.csv",           # eps_{i,t} = (r - mu)/sigma
    "cond_vol":      TV2_DIR / "cond_vol.csv",            # sigma_{i,t} (đơn vị: lợi suất ngày, thập phân)
    "sigma_fcst":    TV2_DIR / "sigma_forecast.csv",      # sigma_{i,T+1}
    # TV3 -> TV4, TV5
    "dcc_params":    TV3_DIR / "dcc_params.csv",
    "dcc_npz":       TV3_DIR / "dcc_matrices.npz",        # dates, tickers, R[t], H[t], R_fcst, H_fcst
    "dyn_corr":      TV3_DIR / "dynamic_correlations.csv",
    # TV4 -> TV5
    "var_es":        TV4_DIR / "var_es_timeseries.csv",
    "backtest":      TV4_DIR / "backtest_results.csv",
}


# ============================================================================
# 2. THAM SỐ CHUNG
# ============================================================================
TRADING_DAYS = 252
ALPHA = 0.05                  # mức ý nghĩa cho các kiểm định thống kê
LB_LAGS = [5, 10, 20]         # độ trễ Ljung-Box

CONF_LEVELS = [0.95, 0.99]    # mức tin cậy VaR/ES
HS_WINDOW = 250               # cửa sổ lăn Historical Simulation
BASEL_WINDOW = 250            # Basel: 250 ngày gần nhất, VaR 99%

# Tỷ trọng danh mục. None = tỷ trọng bằng nhau (0.2 x 5).
# Muốn dùng tỷ trọng vốn hoá: điền MARKET_CAP (đơn vị tuỳ ý, ví dụ nghìn tỷ VND) cho đủ 5 mã.
WEIGHTS = None
MARKET_CAP = {}               # ví dụ: {"VCB": 480, "VHM": 170, "FPT": 190, "HPG": 170, "MWG": 90}

# Giai đoạn căng thẳng (TV5) – theo outline
STRESS_PERIODS = {
    "Covid-19 (02–04/2020)":            ("2020-02-01", "2020-04-30"),
    "Trái phiếu & lãi suất (04–11/2022)": ("2022-04-01", "2022-11-30"),
}

# Cặp cổ phiếu vẽ tương quan động (TV3) – mã nào không có trong dữ liệu sẽ tự bỏ qua
CORR_PAIRS = [("VCB", "VHM"), ("HPG", "FPT")]

RANDOM_SEED = 42


# ============================================================================
# 3. HÀM TIỆN ÍCH DÙNG CHUNG
# ============================================================================
def require(path: Path, who: str):
    """Báo lỗi dễ hiểu khi file đầu vào chưa có (do chưa chạy notebook trước)."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Không thấy {path}.\n=> Hãy chạy notebook {who} trước.")
    return path


def read_panel(path: Path) -> pd.DataFrame:
    """Đọc CSV dạng rộng: index = Date, cột = mã cổ phiếu."""
    return pd.read_csv(path, index_col="Date", parse_dates=True).sort_index()


def get_weights(tickers) -> pd.Series:
    """Trả về vector tỷ trọng w (tổng = 1) theo đúng thứ tự tickers."""
    tickers = list(tickers)
    if WEIGHTS is not None:
        w = pd.Series(WEIGHTS, dtype=float).reindex(tickers)
    elif MARKET_CAP and all(t in MARKET_CAP for t in tickers):
        w = pd.Series(MARKET_CAP, dtype=float).reindex(tickers)
    else:
        w = pd.Series(1.0, index=tickers)
    if w.isna().any():
        raise ValueError(f"Thiếu tỷ trọng cho: {list(w.index[w.isna()])}")
    return w / w.sum()


def ljung_box(x, lags=LB_LAGS) -> pd.DataFrame:
    """
    Kiểm định Ljung-Box (viết tay, không cần statsmodels).
    Q(m) = n(n+2) * sum_{k=1..m} rho_k^2 / (n-k)  ~  chi2(m) dưới H0: không tự tương quan đến trễ m.
    """
    x = np.asarray(pd.Series(x).dropna(), dtype=float)
    n = len(x)
    xc = x - x.mean()
    denom = np.sum(xc ** 2)
    maxlag = max(lags)
    rho = np.array([np.sum(xc[k:] * xc[:-k]) / denom for k in range(1, maxlag + 1)])
    out = []
    for m in lags:
        q = n * (n + 2) * np.sum(rho[:m] ** 2 / (n - np.arange(1, m + 1)))
        out.append({"lag": m, "Q": q, "p-value": stats.chi2.sf(q, m)})
    return pd.DataFrame(out).set_index("lag")


def shade_stress(ax, alpha=0.15):
    """Tô nền các giai đoạn khủng hoảng lên một trục thời gian."""
    colors = ["tab:red", "tab:orange", "tab:purple"]
    for (name, (a, b)), c in zip(STRESS_PERIODS.items(), colors):
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=c, alpha=alpha, label=name)


def print_paths():
    print("BASE_DIR  :", BASE_DIR)
    print("INPUT_DIR :", INPUT_DIR, "| tồn tại:", INPUT_DIR.exists())
    print("OUTPUT_DIR:", OUTPUT_DIR)
