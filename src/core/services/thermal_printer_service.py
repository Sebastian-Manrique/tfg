from escpos.printer import Serial
from datetime import datetime
from src.core.repository.code_repository import CodeRepository


class ThermalPrinterService:
    def __init__(self, printer: Serial = None, logger=None, code_repository: CodeRepository = None):
        """
        Service that manages coupon printing using ESC/POS printer.
        """
        self.printer = printer
        self.logger = logger
        self.code_repository = code_repository

    def center_text(self, text: str, width: int = 32) -> str:
        """
        Center align fixed-width text.
        """
        lines = text.strip().split("\n")
        centered_lines = []
        for line in lines:
            padding = max((width - len(line)) // 2, 0)
            centered_lines.append(" " * padding + line.strip())
        return "\n".join(centered_lines) + "\n"

    def print_summary_coupon(self, summary_id: str, summary: dict):
        """
        Print QR + text for a discount URL.
        """
        if not self.code_repository:
            raise ValueError("CodeRepository is required to get IP")

        ip = self.code_repository._CodeRepository__get_local_ip_from_shell()
        url = f"http://{ip}:5001/summary/{summary_id}"
        euros = summary.get("descuento_total_centimos", 0) / 100

        try:
            if not self.printer:
                print("[DEBUG] Summary coupon:")
                print(self.center_text(""))
                print(self.center_text("Escanea o visita:"))
                print(url)
            else:
                self.printer.text("\n")
                self.printer.text(self.center_text("DISCOUNT OVERVIEW"))
                self.printer.text(self.center_text(
                    f"Scan or visit: {url}") + "\n")
                self.printer.qr(url, size=9)
                self.printer.text("\n")
                self.printer.text(self.center_text(
                    f"Total discount: {euros:.2f} €"))
                self.printer.text("\n")
                self.printer._raw(b"\x1B\x40")  # Reset

            if self.logger:
                self.logger.info(
                    f"Printed resumen con {summary['plastics_bottles']} botellas, {summary['aluminum_cans']} latas y {euros:.2f} €")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error printing summary coupon: {e}")
            else:
                print(f"[ERROR] Error printing summary coupon: {e}")
