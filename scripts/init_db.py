#!/usr/bin/env python3
"""
Database initialization script.
"""

import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize the database."""
    logger.info("Initializing MongoDB database...")
    init_db()
    logger.info("MongoDB collections and indexes created successfully")


if __name__ == "__main__":
    main()
