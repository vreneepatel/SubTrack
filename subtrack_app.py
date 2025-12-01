# subtrack_app.py – Streamlit UI for school catering with navbar + DB

import os
import pathlib
import pandas as pd
import streamlit as st

from subtrack_core import (
    Order,
    LineItem,
    STORES,
    SCHOOLS,
    SANDWICH_MENU,
    MENU_ITEMS,
    UNIT_PRICES,
    LOGO_PATH,
    export_pdf,
    export_csv,
    init_db,
    fetch_invoices,
    fetch_monthly_totals,
)

st.set_page_config(
    page_title="SubTrack – School Catering",
    page_icon="🥪",
    layout="centered",
)

init_db()

if "order" not in st.session_state:
    st.session_state.order = None
if "sides" not in st.session_state:
    st.session_state.sides = []

# ---------- NAVBAR ----------
st.sidebar.title("SubTrack")
page = st.sidebar.radio(
    "Go to",
    ["Create Invoice", "View Past Invoices", "Price List", "Admin Settings"],
)


def render_header(title: str):
    cols = st.columns([1, 5])
    with cols[0]:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)
    with cols[1]:
        st.markdown(f"## {title}")


# ---------- PAGE 1: CREATE INVOICE ----------

def page_create_invoice():
    render_header("School Catering Order")

    with st.container():
        store_choice = st.selectbox(
            "Select store",
            [f"{k} - {v['display']}" for k, v in STORES.items()],
            index=0,
            key="store",
        )
        store_key = store_choice.split(" - ")[0]

        school_names = list(SCHOOLS.keys())
        school_name = st.selectbox(
            "Select school",
            school_names,
            index=0,
            key="school_name",
        )
        school_data = SCHOOLS.get(school_name, {})
        contact_name = school_data.get("contact_name", "")
        contact_email = school_data.get("contact_email", "")

        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**School contact:** {contact_name or '—'}")
        with c2:
            st.write(f"**School email:** {contact_email or '—'}")

        delivery_date = st.date_input("Delivery Date", key="delivery_date")

    st.divider()

    st.subheader("Sandwiches")

    qtys = {}
    for code in SANDWICH_MENU:
        item = MENU_ITEMS[code]
        label = item["label"]
        price = item["price"]

        c1, c2, c3 = st.columns([4, 1, 2])
        with c1:
            st.write(f"**{code} – {label}**")
        with c2:
            st.write(f"${price:.2f}")
        with c3:
            qtys[code] = st.number_input(
                f"{code} quantity",
                min_value=0,
                step=1,
                value=0,
                key=f"qty_{code}",
                label_visibility="collapsed",
            )

    st.divider()

    include_sides = st.checkbox("Include sides/drinks?", key="include_sides")
    if include_sides:
        with st.form("sides_form", clear_on_submit=True):
            sc1, sc2, sc3 = st.columns([2, 1, 1])
            with sc1:
                side_name = st.text_input("Side/Drink name")
            with sc2:
                side_price = st.number_input("Price ($)", min_value=0.0, step=0.01)
            with sc3:
                side_qty = st.number_input("Qty", min_value=0, step=1)
            add_side = st.form_submit_button("Add Side")
            if add_side and side_name:
                st.session_state.sides.append(
                    LineItem(name=side_name, qty=side_qty, unit_price=side_price)
                )
        if st.session_state.sides:
            st.write("Current sides/drinks:")
            for i, s in enumerate(st.session_state.sides, start=1):
                st.write(
                    f"{i}. {s.qty} × {s.name} @ ${s.unit_price:.2f} = ${s.qty * s.unit_price:.2f}"
                )
            if st.button("Clear sides/drinks"):
                st.session_state.sides = []
    else:
        st.session_state.sides = []

    st.divider()

    with st.form("calc_form"):
        submitted = st.form_submit_button("Calculate Total")
        if submitted:
            items = []
            for code in SANDWICH_MENU:
                qty = qtys[code]
                if qty > 0:
                    price = UNIT_PRICES.get(code, 0.0)
                    items.append(LineItem(name=code, qty=qty, unit_price=price))
            if st.session_state.sides:
                items.extend(st.session_state.sides)

            st.session_state.order = Order(
                store_key=store_key,
                school_name=school_name,
                event_date=str(delivery_date),
                items=items,
            )

    if st.session_state.order:
        order = st.session_state.order
        st.success(
            f"Subtotal: ${order.subtotal:.2f}   |   Total: ${order.total:.2f}"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Download PDF Invoice"):
                pdf_path = export_pdf(order)
                if pdf_path:
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="Click to download",
                            data=f.read(),
                            file_name=pathlib.Path(pdf_path).name,
                            mime="application/pdf",
                        )
        with col2:
            if st.button("Export CSV"):
                csv_path = export_csv(order)
                st.success(f"CSV saved: {csv_path}")


# ---------- PAGE 2: VIEW PAST INVOICES ----------

def page_view_invoices():
    render_header("View Past Invoices")

    rows = fetch_invoices(limit=500)
    if not rows:
        st.info("No invoices recorded yet.")
        return

    df = pd.DataFrame(
        rows,
        columns=[
            "ID",
            "Created At",
            "School",
            "Store",
            "Delivery Date",
            "Subtotal",
            "Total",
            "Invoice #",
        ],
    )

    st.subheader("Invoices")
    st.dataframe(df, use_container_width=True)

    st.subheader("Monthly Totals")
    mrows = fetch_monthly_totals()
    if mrows:
        mdf = pd.DataFrame(mrows, columns=["Year-Month", "Total"])
        st.table(mdf)
        st.bar_chart(mdf.set_index("Year-Month"))
    else:
        st.info("No monthly totals yet.")


# ---------- PAGE 3: PRICE LIST ----------

def page_price_list():
    render_header("Price List")

    data = []
    for code in SANDWICH_MENU:
        item = MENU_ITEMS[code]
        data.append(
            {
                "Code": code,
                "Description": item["label"],
                "Price": f"${item['price']:.2f}",
            }
        )
    df = pd.DataFrame(data)
    st.table(df)


# ---------- PAGE 4: ADMIN SETTINGS (placeholder) ----------

def page_admin_settings():
    render_header("Admin Settings")
    st.info("Admin settings coming later. For now, everything is hard-coded in subtrack_core.py.")
    st.write("- Update prices in `MENU_ITEMS`")
    st.write("- Update schools, contacts, and times in `SCHOOLS`")
    st.write("- Stores are in `STORES`")


# ---------- PAGE ROUTER ----------

if page == "Create Invoice":
    page_create_invoice()
elif page == "View Past Invoices":
    page_view_invoices()
elif page == "Price List":
    page_price_list()
elif page == "Admin Settings":
    page_admin_settings()
