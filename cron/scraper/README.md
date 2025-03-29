# Scraper & Proxy Setup

This document explains how to set up a proxy server to capture network traffic, process it with our scraper package, and stream the results to the production database.

---

## 1. Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)
- **mitmproxy** (for capturing network traffic)
- **Chrome** (or another browser with configurable proxy settings)

Install `mitmproxy` with:

```bash
pip install mitmproxy
```

---

## 2. Project Setup

1. **Clone or download** the repository containing the scraper code.
2. **Navigate** to the repository folder:
   ```bash
   cd scraper
   ```
3. **Install Python dependencies** from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

---

## 3. Starting the Proxy

1. **Start `mitmproxy`** on port `8080` and record traffic to a file named `traffic.mitm`:
   ```bash
   mitmproxy -p 8080 -w traffic.mitm
   ```
2. **Keep the terminal open** while `mitmproxy` is running.

---

## 4. Configuring the Browser

### For Google Chrome:

1. Open **Chrome Settings**.
2. Navigate to **Advanced** > **System** > **Open your computer’s proxy settings**.
3. **Enable manual proxy configuration**:
   - **Address**: `127.0.0.1`
   - **Port**: `8080`
4. Apply the changes.

_For other browsers or operating systems, refer to their specific documentation on setting a manual proxy._

---

## 5. Capturing Traffic

1. With `mitmproxy` running and your browser configured, **visit the betting sites** of interest (e.g., Bet365).
2. **Verify** that `mitmproxy` is capturing the traffic.
3. Once done, **stop `mitmproxy`** (Ctrl+C or close the terminal).

> **Note:** For HTTPS traffic, you might need to install the `mitmproxy` certificate. Refer to the [mitmproxy documentation](https://docs.mitmproxy.org/stable/concepts-certificates/) if required.

---

## 6. Running the Scraper

After capturing the traffic:

1. Ensure you are in the repository folder (e.g., `cd scraper`).
2. **Run the scraper** using the CLI. For a single `traffic.mitm` file, use:
   ```bash
   python main.py --file traffic.mitm
   ```
   To process all `.mitm` files in a directory:
   ```bash
   python main.py --dir path/to/mitm_files
   ```
3. The scraper will:
   - Parse the captured traffic.
   - Route each URL to its corresponding parser.
   - Stream the processed data to your production database.

---

## 7. Additional Information

- **Troubleshooting**:
  - **No traffic captured**: Check your browser's proxy settings.
  - **HTTPS issues**: Ensure the `mitmproxy` certificate is installed.
  - **Parser errors**: Confirm that your parsers are correctly imported and registered.
- **Automation**:
  - For periodic execution (e.g., via cron), create a shell script such as:
    ```bash
    #!/usr/bin/env bash
    python main.py --file traffic.mitm
    ```
    Make it executable with:
    ```bash
    chmod +x bet-cron.sh
    ```

---

## 8. Conclusion

By following these steps, you can:

- Set up a proxy server with `mitmproxy`.
- Capture network traffic from betting sites.
- Use the scraper to parse and stream data to your database.

For further details, refer to the code comments and [mitmproxy documentation](https://docs.mitmproxy.org/).

Happy scraping!
