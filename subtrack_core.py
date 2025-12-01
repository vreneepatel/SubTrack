def export_order_form(order: Order, filepath: Optional[str] = None) -> Optional[str]:
    """
    Generate an ORDER FORM PDF: same layout as invoice but
    without prices or money totals. Still includes temps/signatures.
    """
    if FPDF is None:
        print("fpdf2 not installed. Skipping order form PDF export.")
        return None

    out_dir = os.path.join(os.getcwd(), "invoices")
    os.makedirs(out_dir, exist_ok=True)
    if not filepath:
        safe_school = "".join(
            c for c in order.school_name if c.isalnum() or c in (" ", "-", "_")
        )
        date_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(out_dir, f"order_form_{safe_school}_{date_tag}.pdf")

    store = STORES[order.store_key]
    school = SCHOOLS.get(order.school_name, {})
    meta = _invoice_meta(order)  # reuse same number + date

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

    # logo + store info
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
    pdf.cell(
        right_x - left_x - 12,
        14,
        pdf_safe("Shephali Patel and Digna Patel"),
        ln=1,
    )
    pdf.set_x(text_x)
    pdf.cell(
        right_x - left_x - 12,
        14,
        pdf_safe("Phone: (904) 866-9497 or (904) 887-7130"),
        ln=1,
    )
    pdf.set_x(text_x)
    pdf.cell(
        right_x - left_x - 12,
        14,
        pdf_safe(f"Email: {store['email']}"),
        ln=1,
    )
    pdf.set_text_color(0)

    # ORDER FORM box (top right)
    box_y = y0
    pdf.set_xy(right_x, box_y)
    pdf.set_fill_color(GREY, GREY, GREY)
    pdf.set_text_color(255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(RIGHT_W, RIGHT_LABEL_H, "ORDER FORM", align="C", ln=1, fill=True)

    pdf.set_text_color(0)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(right_x)
    pdf.cell(RIGHT_W / 2, RIGHT_ROW_H, "Order #", border=1)
    pdf.cell(RIGHT_W / 2, RIGHT_ROW_H, pdf_safe(meta["number"]), align="R", border=1, ln=1)

    pdf.set_x(right_x)
    pdf.cell(RIGHT_W / 2, RIGHT_ROW_H, "Delivery Date", border=1)
    pdf.cell(RIGHT_W / 2, RIGHT_ROW_H, meta["issued"], align="R", border=1, ln=1)

    delivery_time_raw = school.get("delivery_time", "")
    delivery_time = delivery_time_raw
    if "@" in delivery_time_raw:
        # strip weekday, keep time part after '@'
        delivery_time = delivery_time_raw.split("@", 1)[1].strip()
    pdf.set_x(right_x)
    pdf.cell(RIGHT_W / 2, RIGHT_ROW_H, "Delivery Time", border=1)
    pdf.cell(RIGHT_W / 2, RIGHT_ROW_H, pdf_safe(delivery_time), align="R", border=1, ln=1)

    header_bottom = max(text_y + 16 * 3, box_y + RIGHT_LABEL_H + 2 * RIGHT_ROW_H) + 10
    pdf.set_xy(left_x, header_bottom)
    pdf.set_draw_color(BORDER, BORDER, BORDER)
    pdf.cell(page_w - 2 * PAGE_MARGIN, 0, "", border="B")
    pdf.ln(16)

    # school block
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
        sch_time_raw = school.get("delivery_time", "")
        sch_time = sch_time_raw
        if "@" in sch_time_raw:
            sch_time = sch_time_raw.split("@", 1)[1].strip()
        pdf.cell(
            360,
            14,
            pdf_safe(f"Phone: {sch_phone}   Delivery Time: {sch_time}"),
            ln=1,
        )
        pdf.set_x(left_x)
        sch_email = school.get("contact_email", "")
        pdf.cell(360, 14, pdf_safe(f"Email: {sch_email}"), ln=1)

    pdf.set_x(left_x)
    pdf.cell(360, 14, f"Delivery Date: {fmt_mmddyyyy(order.event_date)}", ln=1)

    pdf.ln(12)

    # table header (no price columns)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(LIGHT, LIGHT, LIGHT)
    pdf.set_x(left_x)
    pdf.cell(COL_DATE, ROW_H, "DELIVERY DATE", border=1, fill=True)
    pdf.cell(COL_DESC, ROW_H, "# OF SANDWICHES", border=1, fill=True)
    pdf.cell(COL_PRICE, ROW_H, "", border=1, fill=True)  # blank price col
    pdf.cell(COL_QTY, ROW_H, "QTY", border=1, align="R", fill=True)
    pdf.cell(COL_TOTAL, ROW_H, "", border=1, fill=True)  # blank total col
    pdf.ln(ROW_H)

    # table rows (no money values)
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
        pdf.cell(COL_PRICE, ROW_H, "", border=1, align="R")  # blank
        pdf.cell(COL_QTY, ROW_H, f"{it.qty}", border=1, align="R")
        pdf.cell(COL_TOTAL, ROW_H, "", border=1, align="R")  # blank
        pdf.ln(ROW_H)

    pdf.ln(16)

    # footer: temps + signatures + note (same as invoice)
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
            "Thank you for your business. Please contact us if you have any "
            "questions regarding this order."
        ),
    )
    pdf.set_text_color(0)

    pdf.output(filepath)
    return os.path.abspath(filepath)
