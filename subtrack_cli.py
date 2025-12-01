# subtrack_cli.py – simple CLI for school catering orders

from __future__ import annotations

from typing import List

from subtrack_core import (
    Order,
    LineItem,
    STORES,
    SCHOOLS,
    SANDWICH_MENU,
    MENU_ITEMS,
    UNIT_PRICES,
    export_pdf,
    export_csv,
    fmt_mmddyyyy,
)


def prompt_choice(prompt: str, options: List[str]) -> str:
    while True:
        print(prompt)
        for i, opt in enumerate(options, start=1):
            print(f"  {i}) {opt}")
        s = input("Enter number: ").strip()
        try:
            idx = int(s)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except ValueError:
            pass
        print("Please enter a valid number.\n")


def prompt_date(prompt: str) -> str:
    s = input(f"{prompt} (MM-DD-YYYY or YYYY-MM-DD): ").strip()
    if not s:
        return ""
    return fmt_mmddyyyy(s)


def prompt_int(prompt: str, min_val: int = 0) -> int:
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
            if v < min_val:
                print(f"Enter a number >= {min_val}.")
                continue
            return v
        except ValueError:
            print("Enter a whole number.")


def prompt_yes_no(prompt: str) -> bool:
    while True:
        s = input(prompt + " (y/n): ").strip().lower()
        if s in {"y", "yes"}:
            return True
        if s in {"n", "no"}:
            return False
        print("Please answer y or n.")


def main() -> None:
    print("\n=== SubTrack – School Catering (CLI) ===\n")

    # store
    store_keys = list(STORES.keys())
    store_opts = [f"{k} - {STORES[k]['display']}" for k in store_keys]
    chosen_store = prompt_choice("Select store:", store_opts)
    store_key = chosen_store.split(" - ")[0]

    # school
    school_names = list(SCHOOLS.keys())
    school_name = prompt_choice("Select school:", school_names)

    # delivery date
    delivery_date = prompt_date("Delivery date")
    print()

    # quantities for menu items
    print("Enter sandwich quantities (press Enter for 0):")
    items: List[LineItem] = []
    for code in SANDWICH_MENU:
        label = MENU_ITEMS[code]["label"]
        price = UNIT_PRICES[code]
        qty_str = input(f"{code} - {label} @ ${price:.2f} qty: ").strip()
        if not qty_str:
            qty = 0
        else:
            try:
                qty = int(qty_str)
            except ValueError:
                print("  Not a number, treating as 0.")
                qty = 0
        if qty > 0:
            items.append(LineItem(name=code, qty=qty, unit_price=price))

    if not items:
        print("\nNo items entered. Exiting.\n")
        return

    order = Order(
        store_key=store_key,
        school_name=school_name,
        event_date=delivery_date,
        items=items,
    )

    print("\n--- Summary ---")
    for it in order.items:
        label = MENU_ITEMS[it.name]["label"]
        line_total = it.line_total
        print(f"{it.qty} x {it.name} - {label} @ ${it.unit_price:.2f} = ${line_total:.2f}")
    print(f"\nSubtotal: ${order.subtotal:.2f}")
    print(f"Delivery (10%): ${order.delivery:.2f}")
    print(f"Total: ${order.total:.2f}\n")

    if prompt_yes_no("Export CSV file?"):
        csv_path = export_csv(order)
        print(f"CSV saved to: {csv_path}")

    if prompt_yes_no("Generate PDF invoice?"):
        pdf_path = export_pdf(order)
        if pdf_path:
            print(f"PDF saved to: {pdf_path}")

    print("\nDone.\n")


if __name__ == "__main__":
    main()