import sqlite3
import json
import os
import time
import uuid

def _conv_key(u1: str, u2: str) -> str:
    return "__".join(sorted([u1, u2]))
