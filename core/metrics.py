def formatiraj_velicinu(bajti):
    """Pretvara bajte u čitljiv format"""
    if bajti < 1024:
        return f"{bajti} B"
    elif bajti < 1024 ** 2:
        return f"{bajti / 1024:.2f} KB"
    elif bajti < 1024 ** 3:
        return f"{bajti / 1024**2:.2f} MB"
    else:
        return f"{bajti / 1024**3:.2f} GB"


def formatiraj_vreme(sekunde):
    """Pretvara sekunde u čitljiv format"""
    if sekunde < 60:
        return f"{sekunde:.1f} sekundi"
    else:
        minuti = int(sekunde // 60)
        sek = sekunde % 60
        return f"{minuti} min {sek:.0f} sek"