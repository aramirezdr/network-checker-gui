# Network Connection Checker

## Overview

Network Connection Checker is a Python-based GUI application that helps users check their network connectivity status, including IP address, network interface, default gateway, and DNS resolution.

## Features

- Display local IP address and network interface.
- Show the default gateway and perform a ping test.
- Resolve domain names using DNS.
- Detect Windows logon server.
- Modern GUI built with **CustomTkinter**.

## Requirements

Make sure you have the following dependencies installed:

- Python 3.x
- `customtkinter`
- `psutil`
- `tk`

You can install the required dependencies using:

```sh
pip install customtkinter psutil tk
```

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/network-checker.git
   ```
2. Navigate to the project folder:
   ```sh
   cd network-checker
   ```
3. Run the application:
   ```sh
   pythonw network_checker.pyw
   ```

## Usage

1. Click on **"Check Connection"** to analyze network connectivity.
2. The tool will display:
   - Your IP address and network interface.
   - Your default gateway and ping test results.
   - DNS resolution for `google.com`.
   - Logon server (Windows only).

## Screenshot

(Add a screenshot of the application here)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributions

Feel free to contribute by submitting issues or pull requests.

## Author

Your Name (@aramirezdr)

