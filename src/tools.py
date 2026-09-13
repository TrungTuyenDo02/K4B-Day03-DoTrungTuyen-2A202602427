"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA
# ==============================================================================

TOOLS_SCHEMA = [
    # --------------------------------------------------------------------------
    # Tool 1: Tra cứu hồ sơ + tình trạng đóng quỹ của thành viên
    # --------------------------------------------------------------------------
    {
        "name": "member_query",
        "description": "Tra cứu hồ sơ thành viên và tình trạng đóng quỹ của một thành viên trong đội bóng bằng mã thành viên.",
        "parameters": {
            "type": "object",
            "properties": {
                "member_id": {
                    "type": "string",
                    "description": "Mã thành viên cần tra cứu (ví dụ: 'TM001')"
                }
            },
            "required": ["member_id"]
        }
    },

    # --------------------------------------------------------------------------
    # Tool 2: Đặt lịch nhắc thu quỹ gắn với buổi tập/thi đấu
    # --------------------------------------------------------------------------
    {
        "name": "schedule_fee_reminder",
        "description": "Đặt lịch nhắc một thành viên đóng quỹ đội bóng, gắn với thời gian và địa điểm của buổi tập luyện hoặc thi đấu.",
        "parameters": {
            "type": "object",
            "properties": {
                "member_id": {
                    "type": "string",
                    "description": "Mã thành viên cần nhắc đóng quỹ (ví dụ: 'TM001')"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian diễn ra buổi tập/thi đấu để nhắc thu quỹ, theo định dạng 'HH:MM DD/MM/YYYY' (ví dụ: '18:00 20/09/2026')"
                },
                "location": {
                    "type": "string",
                    "description": "Địa điểm diễn ra buổi tập/thi đấu, nơi sẽ thu quỹ trực tiếp (ví dụ: 'Sân bóng Thành Công')"
                },
                "event_type": {
                    "type": "string",
                    "enum": ["tap_luyen", "thi_dau"],
                    "description": "Loại sự kiện gắn với việc thu quỹ: 'tap_luyen' (buổi tập) hoặc 'thi_dau' (trận đấu)"
                }
            },
            "required": ["member_id", "datetime_str", "location", "event_type"]
        }
    },

    # --------------------------------------------------------------------------
    # Tool 3: Cập nhật trạng thái thành viên (mới / nghỉ / quay lại)
    # --------------------------------------------------------------------------
    {
        "name": "update_member_status",
        "description": "Cập nhật trạng thái tham gia của một thành viên trong đội bóng: thêm mới, cho nghỉ, hoặc cho quay lại đội.",
        "parameters": {
            "type": "object",
            "properties": {
                "member_id": {
                    "type": "string",
                    "description": "Mã thành viên cần cập nhật (ví dụ: 'TM003'). Nếu là thành viên hoàn toàn mới, hệ thống sẽ tự tạo hồ sơ."
                },
                "full_name": {
                    "type": "string",
                    "description": "Họ tên đầy đủ của thành viên (bắt buộc khi thêm mới, không bắt buộc khi cập nhật trạng thái)"
                },
                "new_status": {
                    "type": "string",
                    "enum": ["moi_them", "nghi", "quay_lai"],
                    "description": "Trạng thái mới cần cập nhật: 'moi_them' (thêm thành viên mới), 'nghi' (cho nghỉ), 'quay_lai' (cho quay lại đội)"
                },
                "position": {
                    "type": "string",
                    "description": "Vị trí thi đấu của thành viên (ví dụ: 'Tiền đạo', 'Thủ môn'). Chỉ cần khi thêm mới."
                }
            },
            "required": ["member_id", "new_status"]
        }
    },

    # --------------------------------------------------------------------------
    # Tool 4: Tra cứu/tổng hợp ngân sách đội bóng (thu - chi)
    # --------------------------------------------------------------------------
    {
        "name": "get_team_budget_summary",
        "description": "Tra cứu và tổng hợp tình hình ngân sách đội bóng trong một khoảng thời gian: tổng thu (quỹ đã đóng), tổng chi, và số dư hiện tại.",
        "parameters": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "integer",
                    "description": "Tháng cần tổng hợp ngân sách (1-12). Nếu không cung cấp, mặc định lấy tháng hiện tại."
                },
                "year": {
                    "type": "integer",
                    "description": "Năm cần tổng hợp ngân sách (ví dụ: 2026). Nếu không cung cấp, mặc định lấy năm hiện tại."
                }
            },
            "required": []
        }
    },

    # --------------------------------------------------------------------------
    # Tool 5: Dự báo thời tiết cho ngày đá bóng (gọi API thật)
    # --------------------------------------------------------------------------
    {
        "name": "get_weather_forecast",
        "description": "Lấy dự báo thời tiết cho một địa điểm và ngày cụ thể, phục vụ việc quyết định có nên tổ chức buổi tập/thi đấu hay không.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Tên địa điểm hoặc thành phố cần xem dự báo thời tiết (ví dụ: 'Ha Noi', 'Da Nang')"
                },
                "date_str": {
                    "type": "string",
                    "description": "Ngày cần xem dự báo, định dạng 'DD/MM/YYYY' (ví dụ: '20/09/2026')"
                }
            },
            "required": ["location", "date_str"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU
# ==============================================================================

MOCK_DATABASE = {
    "TM001": {
        "full_name": "Nguyễn Văn Hùng",
        "position": "Tiền đạo",
        "status": "Đang tham gia",
        "monthly_fee": 100000,
        "fee_status": "Đã đóng tháng 9/2026",
        "debt_amount": 0
    },
    "TM002": {
        "full_name": "Phạm Minh Tuấn",
        "position": "Thủ môn",
        "status": "Đang tham gia",
        "monthly_fee": 100000,
        "fee_status": "Còn nợ",
        "debt_amount": 200000
    }
}

# Mô phỏng sổ quỹ: mỗi dòng là 1 giao dịch (thu hoặc chi)
MOCK_LEDGER = [
    {"type": "thu", "amount": 100000, "month": 9, "year": 2026, "note": "Quỹ TM001 tháng 9"},
    {"type": "chi", "amount": 500000, "month": 9, "year": 2026, "note": "Thuê sân tháng 9"},
    {"type": "chi", "amount": 300000, "month": 9, "year": 2026, "note": "Mua bóng, áo đấu"},
]

# API key nên lưu trong biến môi trường, không hardcode trong code thật
OPENWEATHERMAP_API_KEY =  os.getenv("OPENWEATHERMAP_API_KEY")

if not OPENWEATHERMAP_API_KEY:
    raise ValueError("Chưa cấu hình OPENWEATHERMAP_API_KEY trong file .env")

# ==============================================================================
# 3. HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

def execute_member_query(member_id: str) -> str:
    """Tra cứu hồ sơ và tình trạng đóng quỹ theo mã thành viên"""
    member = MOCK_DATABASE.get(member_id.strip().upper())
    if member:
        return json.dumps({
            "status": "SUCCESS",
            "member_id": member_id,
            "data": member
        }, ensure_ascii=False)
    return json.dumps({
        "status": "NOT_FOUND",
        "message": f"Không tìm thấy dữ liệu thành viên có mã '{member_id}'"
    }, ensure_ascii=False)


def execute_schedule_fee_reminder(member_id: str, datetime_str: str, location: str, event_type: str) -> str:
    """Đặt lịch nhắc thu quỹ gắn với buổi tập/thi đấu"""
    event_label = "buổi tập luyện" if event_type == "tap_luyen" else "trận thi đấu"
    return json.dumps({
        "status": "SUCCESS",
        "reminder_id": f"RM-{member_id}-01",
        "member_id": member_id,
        "datetime": datetime_str,
        "location": location,
        "event_type": event_type,
        "message": f"Đã đặt lịch nhắc thành viên {member_id} đóng quỹ tại {event_label} vào lúc {datetime_str}, địa điểm: {location}."
    }, ensure_ascii=False)


def execute_update_member_status(member_id: str, new_status: str, full_name: str = None, position: str = None) -> str:
    """Cập nhật trạng thái thành viên: thêm mới / nghỉ / quay lại"""
    member_id = member_id.strip().upper()
    status_map = {
        "moi_them": "Đang tham gia",
        "nghi": "Đã nghỉ",
        "quay_lai": "Đang tham gia"
    }

    if new_status == "moi_them":
        if member_id in MOCK_DATABASE:
            return json.dumps({
                "status": "ERROR",
                "message": f"Thành viên '{member_id}' đã tồn tại, không thể thêm mới."
            }, ensure_ascii=False)
        if not full_name:
            return json.dumps({
                "status": "ERROR",
                "message": "Thiếu 'full_name' khi thêm thành viên mới."
            }, ensure_ascii=False)
        MOCK_DATABASE[member_id] = {
            "full_name": full_name,
            "position": position or "Chưa xác định",
            "status": "Đang tham gia",
            "monthly_fee": 100000,
            "fee_status": "Chưa đóng",
            "debt_amount": 100000
        }
        return json.dumps({
            "status": "SUCCESS",
            "message": f"Đã thêm thành viên mới '{full_name}' với mã '{member_id}'."
        }, ensure_ascii=False)

    # Trường hợp nghỉ / quay lại: yêu cầu thành viên đã tồn tại
    member = MOCK_DATABASE.get(member_id)
    if not member:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy thành viên có mã '{member_id}' để cập nhật."
        }, ensure_ascii=False)

    member["status"] = status_map[new_status]
    return json.dumps({
        "status": "SUCCESS",
        "member_id": member_id,
        "new_status": member["status"],
        "message": f"Đã cập nhật trạng thái thành viên '{member_id}' thành '{member['status']}'."
    }, ensure_ascii=False)


def execute_get_team_budget_summary(month: int = None, year: int = None) -> str:
    """Tổng hợp thu - chi ngân sách đội bóng theo tháng/năm"""
    now = datetime.now()
    month = month or now.month
    year = year or now.year

    transactions = [t for t in MOCK_LEDGER if t["month"] == month and t["year"] == year]
    total_thu = sum(t["amount"] for t in transactions if t["type"] == "thu")
    total_chi = sum(t["amount"] for t in transactions if t["type"] == "chi")

    return json.dumps({
        "status": "SUCCESS",
        "month": month,
        "year": year,
        "total_thu": total_thu,
        "total_chi": total_chi,
        "balance": total_thu - total_chi,
        "transaction_count": len(transactions)
    }, ensure_ascii=False)


def execute_get_weather_forecast(location: str, date_str: str) -> str:
    """Gọi API OpenWeatherMap thật để lấy dự báo thời tiết"""
    try:
        # Bước 1: Lấy tọa độ từ tên địa điểm (Geocoding API)
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {"q": location, "limit": 1, "appid": OPENWEATHERMAP_API_KEY}
        geo_resp = requests.get(geo_url, params=geo_params, timeout=10)
        geo_data = geo_resp.json()

        if not geo_data:
            return json.dumps({
                "status": "NOT_FOUND",
                "message": f"Không tìm thấy địa điểm '{location}'."
            }, ensure_ascii=False)

        lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

        # Bước 2: Lấy dự báo 5 ngày / 3 giờ (free tier)
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        forecast_params = {
            "lat": lat, "lon": lon,
            "appid": OPENWEATHERMAP_API_KEY,
            "units": "metric", "lang": "vi"
        }
        forecast_resp = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_data = forecast_resp.json()

        # Lọc các bản ghi khớp với ngày yêu cầu
        target_date = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        matched = [
            entry for entry in forecast_data.get("list", [])
            if entry["dt_txt"].startswith(target_date)
        ]

        if not matched:
            return json.dumps({
                "status": "NOT_FOUND",
                "message": f"Không có dữ liệu dự báo cho ngày {date_str} (API free tier chỉ hỗ trợ 5 ngày tới)."
            }, ensure_ascii=False)

        # Lấy bản ghi buổi chiều làm đại diện (phù hợp giờ đá bóng)
        rep = matched[len(matched) // 2]
        return json.dumps({
            "status": "SUCCESS",
            "location": location,
            "date": date_str,
            "temperature_c": rep["main"]["temp"],
            "weather": rep["weather"][0]["description"],
            "rain_probability": rep.get("pop", 0) * 100,
            "wind_speed_ms": rep["wind"]["speed"]
        }, ensure_ascii=False)

    except requests.exceptions.RequestException as e:
        return json.dumps({
            "status": "ERROR",
            "message": f"Lỗi khi gọi API thời tiết: {str(e)}"
        }, ensure_ascii=False)

# Router gọi tool thực tế
TOOL_ROUTER = {
    "member_query": execute_member_query,
    "schedule_fee_reminder": execute_schedule_fee_reminder,
    "update_member_status": execute_update_member_status,
    "get_team_budget_summary": execute_get_team_budget_summary,
    "get_weather_forecast": execute_get_weather_forecast
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)