from escpos.printer import Serial
from datetime import datetime


def init_printer():
    """
    Initialize ESC/POS serial printer via USB.
    """
    return Serial(devfile='/dev/ttyUSB0', baudrate=9600, timeout=1)


def generate_coupon_code() -> str:
    """
    Generate a unique coupon code using the current date and time.
    """
    return f"DESC-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def center_text(text: str, width: int = 32) -> str:
    """
    Simulate center alignment by adding spaces to both sides.
    Assumes fixed-width font and 32 characters per line.
    """
    lines = text.strip().split("\n")
    centered_lines = []
    for line in lines:
        line = line.strip()
        padding = max((width - len(line)) // 2, 0)
        centered_lines.append(" " * padding + line)
    return "\n".join(centered_lines) + "\n"


def test_print_qr(printer):
    """
    Print a test coupon with manual centered text and a large QR.
    """
    coupon_code = generate_coupon_code()
    url = "https://youtu.be/dQw4w9WgXcQ?si=xaSOv3l0CLnrAB5Y"

    # Print header and coupon info (centered)
    printer.text("\n")
    printer.text(center_text("🧾 TEST COUPON 🧾"))
    printer.text(center_text(coupon_code))
    printer.text(center_text("Scan to view:"))
    printer.text("\n")

    # Print large QR code
    printer.qr(url, size=9)  # Max size for visual impact

    printer._raw(b"\x1B\x40")       # ESC @ = reset printer

    print(f"[DEBUG] Printed large QR for: {url} with coupon: {coupon_code}")


if __name__ == "__main__":
    printer = init_printer()
    test_print_qr(printer)
