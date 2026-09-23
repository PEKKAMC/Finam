# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.


class LogicController:
    def __init__(self, user_info: dict):
        self.user_info = user_info

    @staticmethod
    def get_world_currencies() -> list[str]:
        return [
            "AED (د.إ)", "AFN (؋)", "ALL (L)", "AMD (֏)", "ANG (ƒ)", "AOA (Kz)",
            "ARS ($)", "AUD (A$)", "AWG (ƒ)", "AZN (₼)", "BAM (KM)", "BBD ($)",
            "BDT (৳)", "BGN (лв)", "BHD (.د.ب)", "BIF (FBu)", "BMD ($)", "BND (B$)",
            "BOB (Bs.)", "BRL (R$)", "BSD (B$)", "BTN (Nu.)", "BWP (P)", "BYN (Br)",
            "BZD (BZ$)", "CAD (C$)", "CDF (FC)", "CHF (CHF)", "CLP ($)", "CNY (¥)",
            "COP ($)", "CRC (₡)", "CUP ($)", "CVE (Esc)", "CZK (Kč)", "DJF (Fdj)",
            "DKK (kr)", "DOP (RD$)", "DZD (د.ج)", "EGP (£)", "ERN (Nfk)", "ETB (Br)",
            "EUR (€)", "FJD (FJ$)", "FKP (£)", "GBP (£)", "GEL (₾)", "GHS (GH₵)",
            "GIP (£)", "GMD (D)", "GNF (FG)", "GTQ (Q)", "GYD (G$)", "HKD (HK$)",
            "HNL (L)", "HTG (G)", "HUF (Ft)", "IDR (Rp)", "ILS (₪)", "INR (₹)",
            "IQD (ع.د)", "IRR (﷼)", "ISK (kr)", "JMD (J$)", "JOD (د.ا)", "JPY (¥)",
            "KES (KSh)", "KGS (с)", "KHR (៛)", "KMF (CF)", "KPW (₩)", "KRW (₩)",
            "KWD (د.ك)", "KYD (CI$)", "KZT (₸)", "LAK (₭)", "LBP (ل.ل)", "LKR (Rs)",
            "LRD (L$)", "LSL (L)", "LYD (ل.د)", "MAD (د.م.)", "MDL (L)", "MGA (Ar)",
            "MKD (ден)", "MMK (K)", "MNT (₮)", "MOP (MOP$)", "MRU (UM)", "MUR (₨)",
            "MVR (Rf)", "MWK (MK)", "MXN ($)", "MYR (RM)", "MZN (MT)", "NAD (N$)",
            "NGN (₦)", "NIO (C$)", "NOK (kr)", "NPR (रु)", "NZD (NZ$)", "OMR (ر.ع.)",
            "PAB (B/.)", "PEN (S/.)", "PGK (K)", "PHP (₱)", "PKR (₨)", "PLN (zł)",
            "PYG (₲)", "QAR (ر.ق)", "RON (lei)", "RSD (дин.)", "RUB (₽)", "RWF (FRw)",
            "SAR (ر.س)", "SBD (SI$)", "SCR (₨)", "SDG (ج.س.)", "SEK (kr)", "SGD (S$)",
            "SHP (£)", "SLL (Le)", "SOS (Sh)", "SRD ($)", "SSP (£)", "STN (Db)",
            "SYP (£S)", "SZL (L)", "THB (฿)", "TJS (ЅМ)", "TMT (T)", "TND (د.ت)",
            "TOP (T$)", "TRY (₺)", "TTD (TT$)", "TWD (NT$)", "TZS (TSh)", "UAH (₴)",
            "UGX (USh)", "USD ($)", "UYU ($U)", "UZS (сўм)", "VES (Bs.S)", "VND (đ)",
            "VUV (VT)", "WST (WS$)", "XAF (FCFA)", "XCD (EC$)", "XOF (CFA)", "XPF (₣)",
            "YER (﷼)", "ZAR (R)", "ZMW (ZK)", "ZWL (Z$)"
        ]