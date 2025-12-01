# subtrack_app.py – Streamlit UI for school catering orders

import os
import pathlib
import streamlit as st
from subtrack_core import (
    Order,
    LineItem,
    STORES,
    SCHOOLS,
    SANDWICH_MENU,
    MENU_ITEMS,
    UNIT_PRICES,
    export_pdf,
    LOGO_PATH,
)

st.set_page_config(
    page_title="SubTrack – School Catering",
    page_icon="🥪",
    layout="centered",
)

if "order" not in st.session_state:
    st.session_state.order = None
if "sides" not in st.session_state:
    st.session_state.sides = []

# header
cols = st.columns([1, 5])
with cols[0]:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
with cols[1]:
    st.markdown("## SubTrack – School Catering Order")

# store + school + delivery date
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

# sandwiches
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

# optional sides/drinks
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

# calculate
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

# totals + PDF
if st.session_state.order:
    order = st.session_state.order
    st.success(
        f"Subtotal: ${order.subtotal:.2f}   |   Delivery: ${order.delivery:.2f}   |   Total: ${order.total:.2f}"
    )

    if st.button("Generate PDF Invoice"):
        pdf_path = export_pdf(order)
        if pdf_path:
            st.success(f"PDF saved: {pdf_path}")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download PDF",
                    data=f.read(),
                    file_name=pathlib.Path(pdf_path).name,
                    mime="application/pdf",
                )