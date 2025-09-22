#!/usr/bin/env python3
"""Lightweight replay helper.

Prints the most recent inbound event and associated inbound fax (if any).
This is diagnostic only and does not re-post to the app.
"""
import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
from app.db import SessionLocal  # type: ignore


def main():
    from app.db import InboundEvent  # type: ignore
    try:
        with SessionLocal() as db:
            ev = db.query(InboundEvent).order_by(InboundEvent.created_at.desc()).first()
            if not ev:
                print("No inbound events found")
                return
            print(f"last_event: provider_sid={ev.provider_sid} type={ev.event_type} at={ev.created_at}")
    except Exception as e:
        print(f"error: {e}")


if __name__ == '__main__':
    main()

