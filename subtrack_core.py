    if st.session_state.order:
        order = st.session_state.order
        st.success(
            f"Subtotal: ${order.subtotal:.2f}   |   Total: ${order.total:.2f}"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate PDFs (Invoice + Order Form)"):
                invoice_path = export_pdf(order)
                order_form_path = export_order_form(order)

                if invoice_path:
                    with open(invoice_path, "rb") as f:
                        st.download_button(
                            label="Download Invoice",
                            data=f.read(),
                            file_name=pathlib.Path(invoice_path).name,
                            mime="application/pdf",
                            key="dl_invoice",
                        )
                if order_form_path:
                    with open(order_form_path, "rb") as f:
                        st.download_button(
                            label="Download Order Form",
                            data=f.read(),
                            file_name=pathlib.Path(order_form_path).name,
                            mime="application/pdf",
                            key="dl_order_form",
                        )

        with col2:
            if st.button("Export CSV"):
                csv_path = export_csv(order)
                st.success(f"CSV saved: {csv_path}")
