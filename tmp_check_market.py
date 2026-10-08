"""Check marketplace data."""
import sys
sys.path.insert(0, r"D:\西客松\backend")
from app.infra.database import get_session
from app.models.marketplace_item import MarketplaceItem
from sqlmodel import select

session = get_session()
active_items = session.exec(select(MarketplaceItem).where(MarketplaceItem.is_active == True)).all()
print(f"Active marketplace items: {len(active_items)}")
all_items = session.exec(select(MarketplaceItem)).all()
print(f"All marketplace items: {len(all_items)}")
if all_items:
    for item in all_items[:3]:
        print(f"  - {item.id}: {item.name} (active={item.is_active})")