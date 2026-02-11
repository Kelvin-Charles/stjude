#!/usr/bin/env python3
"""Script to reinitialize database - useful after pulling new project folders"""
from app import app, init_db

if __name__ == '__main__':
    print("Reinitializing database...")
    init_db()
    print("Database reinitialization complete!")
