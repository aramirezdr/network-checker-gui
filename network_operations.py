"""
Network operations module with secure subprocess calls and comprehensive error handling.
"""
import os
import platform
import subprocess
import socket
import psutil
import logging
from typing import Optional, Tuple, Dict, Any
from config_manager import ConfigManager


class NetworkChecker:
    """Handles all network diagnostic operations with proper error handling and logging."""
    
    def __init__(self, config: ConfigManager, logger: logging.Logger):
        """
        Initialize NetworkChecker.
        
        Args:
            config: Configuration manager instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.is_windows = platform.system().lower() == 'windows'
    
    def get_default_gateway(self) -> Optional[str]:
        """
        Get the default gateway IP address.
        
        Returns:
            Gateway IP address or None if not found
        """
        try:
            if self.is_windows:
                # SECURITY FIX: Use list-based command instead of shell=True
                result = subprocess.run(
                    ['ipconfig'],
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout,
                    check=False
                )
                output = result.stdout
                
                for line in output.splitlines():
                    if 'Default Gateway' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            gateway = parts[-1]
                            self.logger.info(f"Found default gateway: {gateway}")
                            return gateway
            else:
                # SECURITY FIX: Use list-based command instead of shell=True
                result = subprocess.run(
                    ['ip', 'route'],
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout,
                    check=False
                )
                output = result.stdout
                
                for line in output.splitlines():
                    if line.startswith('default via'):
                        parts = line.split()
                        if len(parts) >= 3:
                            gateway = parts[2]
                            self.logger.info(f"Found default gateway: {gateway}")
                            return gateway
            
            self.logger.warning("Default gateway not found")
            return None
            
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout while getting default gateway")
            return None
        except Exception as e:
            self.logger.error(f"Error getting default gateway: {e}", exc_info=True)
            return None
    
    def get_ip_and_interface(self) -> Tuple[str, str]:
        """
        Get the local IP address and network interface name.
        
        Returns:
            Tuple of (IP address, interface name)
        """
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                        self.logger.info(f"Found IP {addr.address} on interface {interface}")
                        return addr.address, interface
            
            self.logger.warning("No non-loopback IP address found")
            return 'N/A', 'N/A'
            
        except Exception as e:
            self.logger.error(f"Error getting IP and interface: {e}", exc_info=True)
            return 'N/A', 'N/A'
    
    def get_logon_server(self) -> str:
        """
        Get the Windows logon server from environment variable.
        
        Returns:
            Logon server name or 'N/A'
        """
        if self.is_windows:
            try:
                # SECURITY FIX: Use environment variable directly instead of shell command
                logon_server = os.environ.get('LOGONSERVER', 'N/A')
                self.logger.info(f"Logon server: {logon_server}")
                return logon_server
            except Exception as e:
                self.logger.error(f"Error getting logon server: {e}", exc_info=True)
                return 'N/A'
        else:
            return 'N/A'
    
    def ping(self, host: str) -> str:
        """
        Ping a host and return the result.
        
        Args:
            host: Hostname or IP address to ping
            
        Returns:
            Ping output or error message
        """
        try:
            param = '-n' if self.is_windows else '-c'
            # SECURITY FIX: Use list-based command instead of shell=True
            command = ['ping', param, str(self.config.ping_count), host]
            
            self.logger.debug(f"Executing ping command: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                check=False
            )
            
            if result.returncode == 0:
                self.logger.info(f"Ping to {host} successful")
                return result.stdout
            else:
                self.logger.warning(f"Ping to {host} failed with return code {result.returncode}")
                return f'Ping failed (return code: {result.returncode})'
                
        except subprocess.TimeoutExpired:
            error_msg = f'Ping timeout after {self.config.timeout} seconds'
            self.logger.error(f"Ping to {host}: {error_msg}")
            return error_msg
        except FileNotFoundError:
            error_msg = 'Ping command not found'
            self.logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f'Ping error: {str(e)}'
            self.logger.error(f"Ping to {host}: {error_msg}", exc_info=True)
            return error_msg
    
    def dns_query(self, hostname: str) -> str:
        """
        Perform DNS resolution for a hostname.
        
        Args:
            hostname: Hostname to resolve
            
        Returns:
            Resolved IP address or error message
        """
        try:
            # Set socket timeout
            socket.setdefaulttimeout(self.config.timeout)
            
            self.logger.debug(f"Resolving DNS for {hostname}")
            ip_address = socket.gethostbyname(hostname)
            
            self.logger.info(f"DNS resolution for {hostname}: {ip_address}")
            return ip_address
            
        except socket.timeout:
            error_msg = f'DNS timeout after {self.config.timeout} seconds'
            self.logger.error(f"DNS query for {hostname}: {error_msg}")
            return error_msg
        except socket.gaierror as e:
            error_msg = f'DNS resolution failed: {e}'
            self.logger.error(f"DNS query for {hostname}: {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f'DNS error: {str(e)}'
            self.logger.error(f"DNS query for {hostname}: {error_msg}", exc_info=True)
            return error_msg
        finally:
            # Reset socket timeout
            socket.setdefaulttimeout(None)
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all network diagnostic checks.
        
        Returns:
            Dictionary containing all check results
        """
        self.logger.info("Starting network diagnostics")
        
        results = {
            'ip': 'N/A',
            'interface': 'N/A',
            'logon_server': 'N/A',
            'gateway': None,
            'gateway_ping': 'Not checked',
            'dns_results': {}
        }
        
        # Get IP and interface
        ip_address, interface = self.get_ip_and_interface()
        results['ip'] = ip_address
        results['interface'] = interface
        
        # Get logon server
        results['logon_server'] = self.get_logon_server()
        
        # Get and ping gateway
        gateway = self.get_default_gateway()
        results['gateway'] = gateway
        
        if gateway:
            results['gateway_ping'] = self.ping(gateway)
        else:
            results['gateway_ping'] = 'Gateway not found'
        
        # DNS queries
        for dns_server in self.config.dns_servers:
            results['dns_results'][dns_server] = self.dns_query(dns_server)
        
        self.logger.info("Network diagnostics completed")
        return results
