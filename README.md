# Autoconfig Setter

A lightweight, modern Windows desktop utility built with **Python** and **CustomTkinter** to easily toggle and monitor the Windows Wi-Fi AutoConfig service.

![Platform Screenshot](https://img.shields.io/badge/Platform-Windows-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)

[![Download .exe](https://img.shields.io/badge/Download-Latest%20Release-blue?style=for-the-badge&logo=windows)](https://github.com/CodeApple24/Wi-Fi-autoconfig-utility/releases/latest)



## Features
- **Instant Status Monitoring:** Background worker tracks state changes instantly (whether toggled inside the app or externally via terminal/settings).
- **Zero CPU Waste:** Uses a low-overhead background thread with sleep intervals (`<1%` CPU utilization on average).
- **Dynamic Interface Detection:** Automatically discovers your active wireless network adapter name (`Wi-Fi`, `Wi-Fi 2`, etc.).
- **Modern UI:** Clean, dark-mode interface styled with CustomTkinter.
- **UAC Elevation:** Automatically requests administrator permissions on startup to execute network configuration commands safely.

## Requirements
- **OS:** Windows 10 or higher
- **Python:** 3.8 or higher (if running from source)
- **CustomTkinter** 5.2.0 or higher (if running from source)

## Installation & Running from Source

- **To use source code:** Install dependencies (Python/CustomTkinter mentioned above), download source code from releases tab, and run.

- **Pre-compiled Executable:** Alternatively, download the .exe from releases tab and run. Only requirement is being on Windows 10 or higher.

## License & Attribution

### License
This project is open-source software licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

### Attributions & Third-Party Credits
This project relies on the following open-source libraries and frameworks:

* **[Python](https://python.org)** — Created by the Python Software Foundation. Licensed under the [PSF License](https://python.org).
  * *Used for: Core programming language and runtime environment.*
* **[CustomTkinter](https://github.com)** — Developed by [Tom Schimansky](https://github.com). Licensed under the [MIT License](https://github.com/blob/master/LICENSE).
  * *Used for: Modern, customizable graphical user interface (GUI) elements.*
