"""Parse GMCORE stdout logs to extract simulation progress."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional


class LogParser:
    """Parse GMCORE log output to determine simulation progress."""

    def __init__(self, total_days: float = 0, total_hours: float = 0):
        """
        Args:
            total_days: Total simulation days (from namelist run_days)
            total_hours: Total simulation hours (from namelist run_hours)
        """
        self.total_seconds = total_days * 86400 + total_hours * 3600
        self.current_day = 0.0
        self.current_hour = 0.0
        self.last_update_time = None
        self.start_time = None

    def parse_line(self, line: str) -> Optional[dict]:
        """Parse a single log line and update state.

        GMCORE prints lines like:
          ==> YYYY-MM-DD HH:MM:SS Day N
          or lines with timing info, step counts, etc.

        Returns dict with parsed info or None if line not informative.
        """
        result = {}

        day_match = re.search(r"[Dd]ay\s+(\d+(?:\.\d+)?)", line)
        if day_match:
            self.current_day = float(day_match.group(1))
            result["day"] = self.current_day

        hour_match = re.search(r"[Hh]our\s+(\d+(?:\.\d+)?)", line)
        if hour_match:
            self.current_hour = float(hour_match.group(1))
            result["hour"] = self.current_hour

        ts_match = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", line)
        if ts_match:
            result["timestamp"] = ts_match.group(1)

        te_match = re.search(r"te\s*=\s*([\d.eE+-]+)", line)
        if te_match:
            result["te"] = float(te_match.group(1))

        tpe_match = re.search(r"tpe\s*=\s*([\d.eE+-]+)", line)
        if tpe_match:
            result["tpe"] = float(tpe_match.group(1))

        if re.search(r"\b(error|ERROR|Error|FATAL|Segmentation|SIGSEGV|abort)\b", line):
            result["error"] = True
            result["error_line"] = line.strip()

        if result:
            self.last_update_time = datetime.now()
            return result
        return None

    def get_progress(self) -> dict:
        """Get current progress as percentage and ETA.

        Returns:
            dict with keys: percent, elapsed_str, eta_str, current_step_str
        """
        if self.total_seconds <= 0:
            return {
                "percent": 0,
                "elapsed_str": "—",
                "eta_str": "—",
                "current_step_str": f"Day {self.current_day:.1f}",
            }

        current_seconds = self.current_day * 86400 + self.current_hour * 3600
        percent = min(100.0, (current_seconds / self.total_seconds) * 100)

        elapsed_str = "—"
        eta_str = "—"
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            elapsed_str = _format_duration(elapsed)
            if percent > 0:
                total_est = elapsed / (percent / 100)
                remaining = total_est - elapsed
                eta_str = _format_duration(max(0, remaining))

        return {
            "percent": round(percent, 1),
            "elapsed_str": elapsed_str,
            "eta_str": eta_str,
            "current_step_str": (
                f"Day {self.current_day:.0f}"
                if self.current_day > 0
                else f"Hour {self.current_hour:.1f}"
            ),
        }

    def set_start(self):
        """Mark simulation start time."""
        self.start_time = datetime.now()


def _format_duration(seconds: float) -> str:
    """Format seconds into HH:MM:SS string."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
