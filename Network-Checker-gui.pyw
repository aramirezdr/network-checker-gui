"""
Network Connection Checker GUI Application

A GUI tool for diagnosing network connectivity issues with proper threading,
error handling, and security measures.
"""
import os
import platform
import subprocess
import socket
import psutil
import customtkinter as ctk
from tkinter import messagebox, Canvas
import threading
from typing import Dict, Any

from config_manager import ConfigManager
from logger_config import setup_logger
from network_operations import NetworkChecker


class NetworkCheckerGUI:
    """Main GUI application for network diagnostics."""
    
    def __init__(self):
        """Initialize the GUI application."""
        # Load configuration
        self.config = ConfigManager()
        
        # Setup logging
        self.logger = setup_logger(
            log_file=self.config.log_file,
            level=self.config.log_level,
            max_bytes=self.config.log_max_bytes,
            backup_count=self.config.log_backup_count
        )
        
        self.logger.info("Network Checker GUI starting")
        
        # Initialize network checker
        self.network_checker = NetworkChecker(self.config, self.logger)
        
        # Threading control
        self.check_thread: threading.Thread = None
        self.is_checking = False
        
        # Setup GUI
        self._setup_gui()
    
    def _setup_gui(self) -> None:
        """Setup the GUI components."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("OBS Network Connection Checker")
        self.root.geometry("700x750")
        
        # Main frame
        frame = ctk.CTkFrame(self.root)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Title
        ctk.CTkLabel(
            frame,
            text="Network Connection Checker",
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        # Network topology map
        map_frame = ctk.CTkFrame(frame)
        map_frame.pack(pady=10, fill="x")
        
        ctk.CTkLabel(
            map_frame,
            text="Network Topology",
            font=("Arial", 12, "bold")
        ).pack(pady=5)
        
        self.canvas = Canvas(
            map_frame,
            width=650,
            height=200,
            bg="#2b2b2b",
            highlightthickness=0
        )
        self.canvas.pack(pady=5)
        
        # Initialize topology map
        self._draw_topology_map()
        
        # Results frame with scrollable area
        results_frame = ctk.CTkScrollableFrame(frame, height=100)
        results_frame.pack(pady=10, fill="both", expand=True)
        
        # Result variables
        self.ip_result = ctk.StringVar()
        ctk.CTkLabel(
            results_frame,
            textvariable=self.ip_result,
            font=("Arial", 12)
        ).pack(anchor="w", padx=10, pady=2)
        
        self.interface_result = ctk.StringVar()
        ctk.CTkLabel(
            results_frame,
            textvariable=self.interface_result,
            font=("Arial", 12)
        ).pack(anchor="w", padx=10, pady=2)
        
        self.logon_server_result = ctk.StringVar()
        ctk.CTkLabel(
            results_frame,
            textvariable=self.logon_server_result,
            font=("Arial", 12)
        ).pack(anchor="w", padx=10, pady=2)
        
        self.gw_result = ctk.StringVar()
        ctk.CTkLabel(
            results_frame,
            textvariable=self.gw_result,
            wraplength=550,
            justify="left",
            font=("Arial", 11)
        ).pack(anchor="w", padx=10, pady=5)
        
        self.dns_result = ctk.StringVar()
        ctk.CTkLabel(
            results_frame,
            textvariable=self.dns_result,
            wraplength=550,
            justify="left",
            font=("Arial", 11)
        ).pack(anchor="w", padx=10, pady=2)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            frame,
            text="Ready",
            font=("Arial", 10),
            text_color="gray"
        )
        self.status_label.pack(pady=5)
        
        # Button frame
        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=10)
        
        self.check_button = ctk.CTkButton(
            button_frame,
            text="Check Connection",
            command=self.start_check,
            width=150
        )
        self.check_button.pack(side="left", padx=5)
        
        self.reset_button = ctk.CTkButton(
            button_frame,
            text="Clear/Reset",
            command=self.reset_app,
            width=150
        )
        self.reset_button.pack(side="left", padx=5)
    
    def _draw_topology_map(self, gw_status="unknown", internet_status="unknown", dc_status="unknown") -> None:
        """
        Draw the network topology map showing connection paths.
        
        Args:
            gw_status: Gateway connection status ("success", "failure", "unknown")
            internet_status: Internet connection status ("success", "failure", "unknown")
            dc_status: Domain Controller connection status ("success", "failure", "unknown")
        """
        # Clear canvas
        self.canvas.delete("all")
        
        # Color mapping
        colors = {
            "success": "#4ade80",  # Green
            "failure": "#f87171",  # Red
            "unknown": "#6b7280"   # Gray
        }
        
        # Node positions
        host_x, host_y = 100, 100
        gw_x, gw_y = 325, 100
        internet_x, internet_y = 550, 50
        dc_x, dc_y = 550, 150
        
        # Draw connection lines
        # Host to Gateway
        gw_color = colors.get(gw_status, colors["unknown"])
        self.canvas.create_line(
            host_x + 60, host_y,
            gw_x - 60, gw_y,
            fill=gw_color,
            width=3,
            arrow="last",
            arrowshape=(10, 12, 5)
        )
        
        # Gateway to Internet
        internet_color = colors.get(internet_status, colors["unknown"])
        self.canvas.create_line(
            gw_x + 60, gw_y - 20,
            internet_x - 60, internet_y + 20,
            fill=internet_color,
            width=3,
            arrow="last",
            arrowshape=(10, 12, 5)
        )
        
        # Gateway to Domain Controller
        dc_color = colors.get(dc_status, colors["unknown"])
        self.canvas.create_line(
            gw_x + 60, gw_y + 20,
            dc_x - 60, dc_y - 20,
            fill=dc_color,
            width=3,
            arrow="last",
            arrowshape=(10, 12, 5)
        )
        
        # Draw nodes
        self._draw_node(host_x, host_y, "Host", "#3b82f6")
        self._draw_node(gw_x, gw_y, "Gateway", "#8b5cf6")
        self._draw_node(internet_x, internet_y, "Internet", internet_color)
        self._draw_node(dc_x, dc_y, "Domain\nController", dc_color)
        
        # Draw status indicators
        self._draw_status_indicator(host_x, host_y + 40, "Active", "#4ade80")
        self._draw_status_indicator(gw_x, gw_y + 40, self._get_status_text(gw_status), gw_color)
        self._draw_status_indicator(internet_x, internet_y + 40, self._get_status_text(internet_status), internet_color)
        self._draw_status_indicator(dc_x, dc_y + 40, self._get_status_text(dc_status), dc_color)
    
    def _draw_node(self, x: int, y: int, label: str, color: str) -> None:
        """
        Draw a network node on the canvas.
        
        Args:
            x: X coordinate of node center
            y: Y coordinate of node center
            label: Node label text
            color: Node color
        """
        # Draw rounded rectangle (node)
        self.canvas.create_oval(
            x - 60, y - 25,
            x + 60, y + 25,
            fill=color,
            outline="white",
            width=2
        )
        
        # Draw label
        self.canvas.create_text(
            x, y,
            text=label,
            fill="white",
            font=("Arial", 10, "bold")
        )
    
    def _draw_status_indicator(self, x: int, y: int, status_text: str, color: str) -> None:
        """
        Draw a status indicator below a node.
        
        Args:
            x: X coordinate
            y: Y coordinate
            status_text: Status text to display
            color: Status color
        """
        self.canvas.create_text(
            x, y,
            text=status_text,
            fill=color,
            font=("Arial", 8)
        )
    
    def _get_status_text(self, status: str) -> str:
        """
        Convert status code to display text.
        
        Args:
            status: Status code ("success", "failure", "unknown")
            
        Returns:
            Display text for status
        """
        status_map = {
            "success": "✓ Connected",
            "failure": "✗ Failed",
            "unknown": "○ Unknown"
        }
        return status_map.get(status, "○ Unknown")
    
    def start_check(self) -> None:
        """Start network check in a background thread."""
        if self.is_checking:
            self.logger.warning("Check already in progress")
            return
        
        self.logger.info("Starting network check")
        self.is_checking = True
        
        # Update UI state
        self.check_button.configure(state="disabled", text="Checking...")
        self.reset_button.configure(state="disabled")
        self.status_label.configure(text="Running diagnostics...", text_color="yellow")
        
        # Clear previous results
        self.reset_app()
        
        # Start background thread
        self.check_thread = threading.Thread(target=self._run_check, daemon=True)
        self.check_thread.start()
    
    def _run_check(self) -> None:
        """Run network checks in background thread."""
        try:
            # Run all network checks
            results = self.network_checker.run_all_checks()
            
            # Update GUI with results (thread-safe)
            self.root.after(0, self._update_results, results)
            
        except Exception as e:
            self.logger.error(f"Error during network check: {e}", exc_info=True)
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self._show_error, error_msg)
        finally:
            # Re-enable buttons
            self.root.after(0, self._check_complete)
    
    def _update_results(self, results: Dict[str, Any]) -> None:
        """
        Update GUI with check results (must be called from main thread).
        
        Args:
            results: Dictionary containing check results
        """
        try:
            # Update IP and interface
            self.ip_result.set(f"IP Address: {results['ip']}")
            self.interface_result.set(f"Network Interface: {results['interface']}")
            self.logon_server_result.set(f"Logon Server: {results['logon_server']}")
            
            # Update gateway ping result
            gateway = results['gateway']
            gateway_ping = results['gateway_ping']
            
            if gateway:
                # Parse ping output for summary
                ping_summary = self._parse_ping_output(gateway_ping)
                self.gw_result.set(f"Gateway: {gateway}\nPing Result: {ping_summary}")
            else:
                self.gw_result.set("Gateway: Not found")
            
            # Update DNS results
            dns_results_text = "DNS Resolution:\n"
            for server, result in results['dns_results'].items():
                dns_results_text += f"  {server} → {result}\n"
            self.dns_result.set(dns_results_text.strip())
            
            # Update topology map based on results
            gw_status = "success" if gateway and "Reply from" in gateway_ping else "failure" if gateway else "unknown"
            
            # Check internet connectivity (based on ping to 8.8.8.8)
            internet_ping = results.get('internet_ping', 'Not checked')
            internet_status = "success" if "Reply from" in internet_ping or internet_ping.startswith("64 bytes") else "failure"
            
            # Check DC connectivity (based on logon server)
            dc_status = "success" if results['logon_server'] and results['logon_server'] != "Not available" else "failure"
            
            # Redraw topology map with updated statuses
            self._draw_topology_map(gw_status, internet_status, dc_status)
            
            self.status_label.configure(text="Check completed successfully", text_color="green")
            self.logger.info("Results updated in GUI")
            
        except Exception as e:
            self.logger.error(f"Error updating results: {e}", exc_info=True)
            self._show_error(f"Error displaying results: {str(e)}")
    
    def _parse_ping_output(self, ping_output: str) -> str:
        """
        Parse ping output to extract key information.
        
        Args:
            ping_output: Raw ping command output
            
        Returns:
            Summarized ping result
        """
        if "Ping failed" in ping_output or "timeout" in ping_output.lower():
            return ping_output
        
        # Extract key lines for Windows
        if platform.system().lower() == 'windows':
            lines = ping_output.split('\n')
            for line in lines:
                if 'Reply from' in line or 'Request timed out' in line:
                    return line.strip()
                if 'Packets:' in line:
                    return line.strip()
        else:
            # For Linux/Mac, show first response line
            lines = ping_output.split('\n')
            for line in lines:
                if 'bytes from' in line.lower():
                    return line.strip()
        
        return "Success"
    
    def _show_error(self, error_msg: str) -> None:
        """
        Show error message to user.
        
        Args:
            error_msg: Error message to display
        """
        self.status_label.configure(text=f"Error: {error_msg}", text_color="red")
        messagebox.showerror("Network Check Error", error_msg)
    
    def _check_complete(self) -> None:
        """Re-enable UI after check completes."""
        self.is_checking = False
        self.check_button.configure(state="normal", text="Check Connection")
        self.reset_button.configure(state="normal")
    
    def reset_app(self) -> None:
        """Clear all results from the display."""
        self.logger.debug("Resetting display")
        self.ip_result.set("")
        self.interface_result.set("")
        self.logon_server_result.set("")
        self.gw_result.set("")
        self.dns_result.set("")
        self.status_label.configure(text="Ready", text_color="gray")
        # Reset topology map to unknown state
        self._draw_topology_map()
    
    def run(self) -> None:
        """Start the GUI main loop."""
        self.logger.info("Starting GUI main loop")
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"GUI error: {e}", exc_info=True)
            raise
        finally:
            self.logger.info("GUI closed")


def main():
    """Main entry point for the application."""
    app = NetworkCheckerGUI()
    app.run()


if __name__ == "__main__":
    main()