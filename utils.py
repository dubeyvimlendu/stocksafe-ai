def format_indian(num):
    if num is None:
        return "—"

    num = float(num)

    # Convert raw numbers to crores/lakhs directly
    if num >= 1_00_00_000:            # 1 Crore = 1,00,00,000
        return f"{num/1_00_00_000:.2f} Cr"
    elif num >= 1_00_000:             # 1 Lakh = 1,00,000
        return f"{num/1_00_000:.2f} L"
    elif num >= 1_000:
        return f"{num/1_000:.2f} K"
    else:
        return f"{num:.2f}"



