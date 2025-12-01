# subtrack_core.py – shared models, menu, schools, CSV + PDF export + CSV invoice log

import os
import csv
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

LOGO_PATH = "Subway Logo.png"
DELIVERY_RATE = 0.10  # kept for future, but not used for schools now
INVOICE_DUE_DAYS = 14  # kept for future if you ever want terms again
INVOICE_LOG_CSV = "invoices_log.csv"  # replaces the SQLite DB

# ------------ MENU ------------

SANDWICH_MENU: List[str] = [
    "M001",
    "M002",
    "M003",
    "M004",
    "M005",
    "M006",
    "M007",
    "M008",
    "M009",
    "M010",
    "M011",
    "M012",
    "M013",
]

MENU_ITEMS: Dict[str, Dict[str, object]] = {
    "M001": {
        "label": '6" White roll. Turkey/Provolone, NO L&T',
        "price": 3.60,
    },
    "M002": {
        "label": '6" White roll. Turkey/Provolone, L&T',
        "price": 3.60,
    },
    "M003": {
        "label": '6" White roll. Turkey/American, NO L&T',
        "price": 3.60,
    },
    "M004": {
        "label": '6" White roll. Turkey/American, L&T',
        "price": 3.60,
    },
    "M005": {
        "label": '6" White roll. Ham/American, L&T',
        "price": 3.50,
    },
    "M006": {
        "label": '6" White roll. Ham/American, NO L&T',
        "price": 3.50,
    },
    "M007": {
        "label": '6" White roll. Ham/Provolone, NO L&T',
        "price": 3.50,
    },
    "M008": {
        "label": '6" White roll. Ham/Provolone, L&T',
        "price": 3.50,
    },
    "M009": {
        "label": '6" White roll. Veggie/Provolone',
        "price": 3.25,
    },
    "M010": {
        "label": '6" White roll. Veggie/American',
        "price": 3.25,
    },
    "M011": {
        "label": '6" White roll. Veggie',
        "price": 3.25,
    },
    "M012": {
        "label": '4" White roll. Ham/American',
        "price": 2.75,
    },
    "M013": {
        "label": '4" White roll. Turkey/American',
        "price": 3.00,
    },
}

UNIT_PRICES: Dict[str, float] = {
    code: float(MENU_ITEMS[code]["price"]) for code in SANDWICH_MENU
}

# ------------ STORES ------------

STORES: Dict[str, Dict[str, str]] = {
    "1": {
        "display": "Shree Ganesh of San Jose",
        "name": "Shree Ganesh of San Jose",
        "phone": "904-367-8404",
        "email": "subwayatsanjose@gmail.com",
        "is_subway": "True",
    },
    "2": {
        "display": "Shree Ganesh of Yulee",
        "name": "Shree Ganesh of Yulee",
        "phone": "904-849-1168",
        "email": "yuleesubway@gmail.com",
        "is_subway": "True",
    },
}

# ------------ SCHOOLS ------------

SCHOOLS: Dict[str, Dict[str, str]] = {
    "Allen Nease High School": {
        "code": "NHS001",
        "manager": "Shannon Bentley",
        "phone": "904-547-8289",
        "address": "10550 Ray Rd, Ponte Vedra Beach, FL 32081",
        "delivery_time": "Thursday @ 10:15am",
        "contact_name": "Shannon Bentley",
        "contact_email": "shannon.bentley@stjohns.k12.fl.us",
    },
    "Bartram Trail High School": {
        "code": "BTHS002",
        "manager": "Sandy Mattox",
        "phone": "904-547-8256",
        "address": "7399 Longleaf Pine Pkwy, St Johns, FL 32259",
        "delivery_time": "Monday @ 10:30am",
        "contact_name": "Sandy Mattox",
        "contact_email": "Sandra.Mattox@stjohns.k12.fl.us",
    },
    "Beachside High School": {
        "code": "BHS003",
        "manager": "Tanya Cassano",
        "phone": "904-547-4417",
        "address": "200 Great Barracuda Wy, St Johns, FL 32259",
        "delivery_time": "Wednesday @ 11:00am",
        "contact_name": "Tanya Cassano",
        "contact_email": "tanya.s.cassano@stjohns.k12.fl.us",
    },
    "Creekside High School": {
        "code": "CHS004",
        "manager": "Lisa Marino",
        "phone": "904-547-7329",
        "address": "100 Knights Ln, St Johns, FL 32259",
        "delivery_time": "Monday @ 9:30am",
        "contact_name": "Lisa Marino",
        "contact_email": "lisa.marino@stjohns.k12.fl.us",
    },
    "Fruit Cove Middle School": {
        "code": "FCMS005",
        "manager": "Diana Lakoskey",
        "phone": "904-547-7886",
        "address": "3180 Race Track Rd, St Johns, FL 32259",
        "delivery_time": "Tuesday @ 9:15am",
        "contact_name": "Diana Lakoskey",
        "contact_email": "diana.lakoskey@stjohns.k12.fl.us",
    },
    "Landrum Middle School": {
        "code": "LMS006",
        "manager": "Michael Howell",
        "phone": "904-547-8421",
        "address": "230 Landrum Ln, Ponte Vedra Beach, FL 32082",
        "delivery_time": "Thursday @ 9:30am",
        "contact_name": "Michael Howell",
        "contact_email": "michael.howell@stjohns.k12.fl.us",
    },
    "Ponte Vedra High School": {
        "code": "PVHS007",
        "manager": "Jill Franzoi",
        "phone": "904-547-7371",
        "address": "460 Davis Park Rd, Ponte Vedra Beach, FL 32081",
        "delivery_time": "Tuesday @ 10:00am",
        "contact_name": "Jill Franzoi",
        "contact_email": "jill.franzoi@stjohns.k12.fl.us",
    },
    "Switzerland Point Middle School": {
        "code": "SPMS008",
        "manager": "Terri Smith",
        "phone": "904-547-8636",
        "address": "777 Greenbriar Rd, Jacksonville, FL 32259",
        "delivery_time": "Tuesday @ 9:00-9:30am",
        "contact_name": "Terri Smith",
        "contact_email": "smitht@stjohns.k12.fl.us",
    },
    "Tocoi Creek High School": {
        "code": "TCHS009",
        "manager": "Tony Carta",
        "phone": "904-547-4277",
        "address": "11200 St. Johns Pkwy, St. Augustine, FL 32092",
        "delivery_time": "Monday @ 10:15am",
        "contact_name": "Tony Carta",
        "contact_email": "Anthony.Carta@stjohns.k12.fl.us",
    },
}

# ------------ DATA MODELS ------------

@dataclass
class LineItem:
    name: str          # item code, e.g. "M001"
    qty: int
    unit_price: float

    @property
    def line_total(self) -> float:
        return round(self.qty * self.unit_price, 2)


@dataclass
class Order:
    store_key: str         # "1" or "2"
    school_name: str       # key into SCHOOLS
    event_date: str        # "YYYY-MM-DD" or "MM-DD-YYYY"
    items: List[LineItem]
    include_delivery: bool = False   # no delivery fee for schools

    @property
    def subtotal(self) -> float:
        return round(sum(i.line_total for i in self.items), 2)

    @property
    def delivery(self) -> float:
        return 0.0

    @property
    def total(self) -> float:
        return self.subtotal

# ------------ HELPERS ------------

def fmt_money(x: float) -> str:
    return f"${x:,.2f}"


def fmt_mmddyyyy(value: str) -> str:
    if not value:
        return value
    v = value.strip()
    for fmt in ("%m-%d-%Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(v, fmt)
            return dt.strftime("%m-%d-%Y")
        except Exception:
            continue
    try:
        dt = datetime.fromisoformat(v)
        return dt.strftime("%m-%d-%Y")
    except Exception:
        return v


def pdf_safe(text: str) -> str:
    if text is None:
        return ""
    return text.encode("ascii", "replace").decode("ascii")


def school_code(name: str) -> str:
    info = SCHOOLS.get(name)
    if info and "code" in info:
        return info["code"]
    return "GEN000"

# ------------ "DB" HELPERS (CSV-BASED) ------------

def init_db() -> None:
    """
    Kept for compatibility with subtrack_app.
    For CSV mode, we don't need to do anything here.
    """
    return


def _ensure_invoice_log_with_header() -> None:
    if not os.path.exists(INVOICE_LOG_CSV):
        with open(INVOICE_LOG_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "created_at",
                    "store_key",
                    "store_name",
                    "school_name",
                    "delivery_date",
                    "subtotal",
                    "total",
                    "invoice_number",
                    "pdf_path",
                ]
            )


def record_invoice(order: Order, invoice_number: str, pdf_path: str) -> None:
    """
    Append one invoice record to invoices_log.csv.
    """
    _ensure_invoice_log_with_header()
    store = STORES[order.store_key]
    created_at = datetime.now().isoformat(timespec="seconds")
    delivery_date_fmt = fmt_mmddyyyy(order.event_date)

    with open(INVOICE_LOG_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                created_at,
                order.store_key,
                store["name"],
                order.school_name,
                delivery_date_fmt,
                f"{order.subtotal:.2f}",
                f"{order.total:.2f}",
                invoice_number,
                pdf_path,
            ]
        )


def fetch_invoices(limit: int = 200):
    """
    Read invoices from invoices_log.csv.
    Returns a list of tuples:
    (ID, created_at, school_name, store_name, delivery_date, subtotal, total, invoice_number)
    """
    if not os.path.exists(INVOICE_LOG_CSV):
        return []

    rows = []
    with open(INVOICE_LOG_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # newest first, based on created_at string
    rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)

    result = []
    for idx, r in enumerate(rows[:limit], start=1):
        created_at = r.get("created_at", "")
        school_name = r.get("school_name", "")
        store_name = r.get("store_name", "")
        delivery_date = r.get("delivery_date", "")
        try:
            subtotal = float(r.get("subtotal", "0") or 0)
        except ValueError:
            subtotal = 0.0
        try:
            total = float(r.get("total", "0") or 0)
        except ValueError:
            total = 0.0
        invoice_number = r.get("invoice_number", "")
        result.append(
            (
                idx,
                created_at,
                school_name,
                store_name,
                delivery_date,
                subtotal,
                total,
                invoice_number,
            )
        )
    return result


def fetch_monthly_totals():
    """
    Group totals by year-month (based on created_at) from invoices_log.csv.
    Returns list of (YYYY-MM, total).
    """
    if not os.path.exists(INVOICE_LOG_CSV):
        return []

    totals: Dict[str, float] = {}
    with open(INVOICE_LOG_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            created_at = row.get("created_at", "")
            if not created_at or len(created_at) < 7:
                continue
            year_month = created_at[:7]  # "YYYY-MM"
            try:
                amount = float(row.get("total", "0") or 0)
            except ValueError:
                amount = 0.0
            totals[year_month] = totals.get(year_month, 0.0) + amount

    # sort newest first
    out = sorted(totals.items(), key=lambda x: x[0], reverse=True)
    return out

# ------------ CSV EXPORT (PER ORDER DETAIL) ------------

def export_csv(order: Order, filepath: Optional[str] = None) -> str:
    if not filepath:
        safe_school = "".join(
            c for c in order.school_name if c.isalnum() or c in (" ", "-", "_")
        )
        date_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"order_{safe_school}_{date_tag}.csv"

    school_info = SCHOOLS.get(order.school_name, {})
    school_code_value = school_info.get("code", "")
    school_contact = school_info.get("contact_name", "")
    school_email = school_info.get("contact_email", "")

    rows = []
    for it in order.items:
        rows.append(
            {
                "School": order.school_name,
                "SchoolCode": school_code_value,
                "DeliveryDate": fmt_mmddyyyy(order.event_date),
                "Store": STORES[order.store_key]["name"],
                "ItemCode": it.name,
                "ItemLabel": MENU_ITEMS[it.name]["label"],
                "Qty": it.qty,
                "UnitPrice": f"{it.unit_price:.2f}",
                "LineTotal": f"{it.line_total:.2f}",
                "Subtotal": f"{order.subtotal:.2f}",
                "Total": f"{order.total:.2f}",
                "SchoolContact": school_contact,
                "SchoolEmail": school_email,
            }
        )

    fieldnames = list(rows[0].keys()) if rows else [
        "School",
        "SchoolCode",
        "DeliveryDate",
        "Store",
        "ItemCode",
        "ItemLabel",
        "Qty",
        "UnitPrice",
        "LineTotal",
        "Subtotal",
        "Total",
        "SchoolContact",
        "SchoolEmail",
    ]

    with open(filepath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    return filepath

# ------------ PDF EXPORT ------------

class InvoicePDF(FPDF):  # type: ignore
    def header(self):
        pass


def _invoice_meta(order: Order) -> dict:
    delivery_str = fmt_mmddyyyy(order.event_date)
    code = school_code(order.school_name)
    inv_num = f"{code}-{delivery_str}"
    return {"number": inv_num, "issued": delivery_str}


def export_pdf(order: Order, filepath: Optional[str] = None) -> Optional[str]:
    if FPDF is None:
        print("fpdf2 not installed. Skipping PDF export.")
        return None

    # no DB init anymore; CSV log will be created on demand

    out_dir = os.path.join(os.getcwd(), "invoices")
    os.makedirs(out_dir, exist_ok=True)
    if not filepath:
        safe_school = "".join(
            c for c in order.school_name if c.isalnum() or c in (" ", "-", "_")
        )
        date_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(out_dir, f"invoice_{safe_school}_{date_tag}.pdf")

    store = STORES[order.store_key]
    school = SCHOOLS.get(order.school_name, {})
    meta = _invoice_meta(order)

    PAGE_MARGIN = 56
    LOGO_H = 52
    ROW_H = 20

    COL_DATE = 90
    COL_DESC = 220
    COL_PRICE = 70
    COL_QTY = 60
    COL_TOTAL = 90
    TABLE_WIDTH = COL_DATE + COL_DESC + COL_PRICE + COL_QTY + COL_TOTAL

    RIGHT_W = 220
    RIGHT_LABEL_H = 24
    RIGHT_ROW_H = 22

    GREY = 60
    LIGHT = 240
    BORDER = 205

    pdf = InvoicePDF(unit="pt", format="Letter")
    pdf.set_auto_page_break(auto=True, margin=PAGE_MARGIN)
    pdf.add_page()
    pdf.set_draw_color(BORDER, BORDER, BORDER)

    page_w = pdf.w
    left_x = PAGE_MARGIN
    right_x = page_w - PAGE_MARGIN - RIGHT_W
    y0 = PAGE_MARGIN

    if os.path.exists(LOGO_PATH):
        try:
            pdf.image(LOGO_PATH, x=left_x, y=y0, h=LOGO_H)
        except Exception:
            pass

    text_x = left_x
    text_y = y0 + LOGO_H + 8
    pdf.set_xy(text_x, text_y)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(right_x - left_x - 12, 16, pdf_safe(store["name"]), ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80)
    pdf.set_x(text_x)
    pdf.cell(right_x - left_x - 12, 14, pdf_safe(f"Phone: {store['phone']}"), ln=1)
    pdf.set_x(text_x)
    pdf.cell(right_x - left_x - 12, 14, pdf_safe(f"Email: {store['email']}"), ln=1)
    pdf.set_text_color(0)

    box_y = y0
    pdf.set_xy(right_x, box_y)
    pdf.set_fill_color(GREY, GREY, GREY)
    pdf.set_text_color(255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(RIGHT_W, RIGHT_LABEL_H, "INVOICE", align="C", ln=1, fill=True)

    pdf.set_text_color(0)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(right_x)
    pdf.cell(RIGHT_W / 2, RIGHT_ROW_H, "Invoice #", border=1)
    pdf.cell(
        RIGHT_W / 2,
        RIGHT_ROW_H,
        pdf_safe(meta["number"]),
        align="R",
        border=1,
        ln=1,
    )
    pdf.set_x(right_x)
    pdf.cell(RIGHT_W / 2, RIGHT_ROW_H, "Date", border=1)
    pdf.cell(RIGHT_W / 2, RIGHT_ROW_H, meta["issued"], align="R", border=1, ln=1)

    header_bottom = max(text_y + 16 * 3, box_y + RIGHT_LABEL_H + 2 * RIGHT_ROW_H) + 10
    pdf.set_xy(left_x, header_bottom)
    pdf.set_draw_color(BORDER, BORDER, BORDER)
    pdf.cell(page_w - 2 * PAGE_MARGIN, 0, "", border="B")
    pdf.ln(16)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_x(left_x)
    pdf.cell(120, 14, "SCHOOL:", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(left_x)
    pdf.cell(360, 14, pdf_safe(order.school_name), ln=1)

    if school:
        pdf.set_x(left_x)
        pdf.cell(360, 14, pdf_safe(school.get("address", "")), ln=1)
        pdf.set_x(left_x)
        mgr = school.get("manager", "")
        if mgr:
            pdf.cell(360, 14, pdf_safe(f"Manager: {mgr}"), ln=1)
        pdf.set_x(left_x)
        sch_phone = school.get("phone", "")
        sch_time = school.get("delivery_time", "")
        pdf.cell(
            360,
            14,
            pdf_safe(f"School Phone: {sch_phone}   Delivery Time: {sch_time}"),
            ln=1,
        )
        pdf.set_x(left_x)
        sch_email = school.get("contact_email", "")
        pdf.cell(360, 14, pdf_safe(f"School Email: {sch_email}"), ln=1)

    pdf.set_x(left_x)
    pdf.cell(360, 14, f"Delivery Date: {fmt_mmddyyyy(order.event_date)}", ln=1)

    pdf.ln(12)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(LIGHT, LIGHT, LIGHT)
    pdf.set_x(left_x)
    pdf.cell(COL_DATE, ROW_H, "DELIVERY DATE", border=1, fill=True)
    pdf.cell(COL_DESC, ROW_H, "# OF SANDWICHES", border=1, fill=True)
    pdf.cell(COL_PRICE, ROW_H, "PRICE", border=1, align="R", fill=True)
    pdf.cell(COL_QTY, ROW_H, "QTY", border=1, align="R", fill=True)
    pdf.cell(COL_TOTAL, ROW_H, "TOTAL", border=1, align="R", fill=True)
    pdf.ln(ROW_H)

    pdf.set_font("Helvetica", "", 10)
    delivery_date_str = fmt_mmddyyyy(order.event_date)
    for it in order.items:
        if it.qty <= 0:
            continue
        label = MENU_ITEMS[it.name]["label"]
        desc = f"{it.name} - {label}"

        pdf.set_x(left_x)
        pdf.cell(COL_DATE, ROW_H, delivery_date_str, border=1)
        pdf.cell(COL_DESC, ROW_H, pdf_safe(desc), border=1)
        pdf.cell(COL_PRICE, ROW_H, fmt_money(it.unit_price), border=1, align="R")
        pdf.cell(COL_QTY, ROW_H, f"{it.qty}", border=1, align="R")
        pdf.cell(COL_TOTAL, ROW_H, fmt_money(it.line_total), border=1, align="R")
        pdf.ln(ROW_H)

    pdf.ln(10)

    def total_row(label: str, value: float, bold: bool = False, fill: bool = False):
        pdf.set_x(left_x + COL_DATE + COL_DESC)
        if bold:
            pdf.set_font("Helvetica", "B", 11)
        else:
            pdf.set_font("Helvetica", "", 10)
        if fill:
            pdf.set_fill_color(GREY, GREY, GREY)
            pdf.set_text_color(255)
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(0)
        pdf.cell(COL_PRICE + COL_QTY, ROW_H, label, border=1, fill=fill)
        pdf.cell(COL_TOTAL, ROW_H, fmt_money(value), border=1, align="R", fill=fill)
        pdf.set_text_color(0)
        pdf.ln(ROW_H)

    total_row("Subtotal", order.subtotal)
    total_row("Total", order.total, bold=True, fill=True)

    pdf.ln(18)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(90)
    pdf.set_x(left_x)
    pdf.multi_cell(
        TABLE_WIDTH,
        12,
        pdf_safe(
            "Contact: Shephali or Digna Patel  |  Phone: "
            f"{store['phone']}  |  Email: {store['email']}"
        ),
    )

    pdf.ln(16)
    pdf.set_text_color(0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_x(left_x)
    pdf.cell(150, 16, "Temperature at the store:", border=0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(200, 16, "__________________", border=0, ln=1)

    pdf.ln(4)
    pdf.set_x(left_x)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(150, 16, "Temperature at delivery:", border=0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(200, 16, "__________________", border=0, ln=1)

    pdf.ln(10)
    pdf.set_x(left_x)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(200, 16, "Store Representative Signature:", border=0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(220, 16, "______________________________", border=0, ln=1)

    pdf.ln(6)
    pdf.set_x(left_x)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(200, 16, "Received by:", border=0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(220, 16, "______________________________", border=0, ln=1)

    pdf.ln(18)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(90)
    pdf.set_x(left_x)
    pdf.multi_cell(
        TABLE_WIDTH,
        12,
        pdf_safe(
            "Thank you for your business. Please contact us through email if you have any "
            "questions regarding this invoice."
        ),
    )
    pdf.set_text_color(0)

    pdf.output(filepath)

    record_invoice(order, meta["number"], filepath)

    return os.path.abspath(filepath)
