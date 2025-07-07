# ⚙️ Earth Engine Processor

Welcome to the **Earth Engine Processor**! This is the backend brain that manages satellite data downloads, processing, and communication with the frontend. 🧠🌐

---

## 🚀 What Does It Do?
- Handles download requests from the frontend
- Processes satellite imagery (cloud masking, tiling, etc.)
- Tracks progress and logs every step
- Reports errors and status updates to the UI
- Supports advanced options for power users

---

## 🛠️ How It Works
1. **Receives download requests** (AOI, satellite, date range, options)
2. **Validates inputs** and checks authentication
3. **Processes imagery**:
   - Cloud masking
   - Tiling and chunking
   - Resolution and band selection
4. **Downloads data** and saves to disk
5. **Updates progress** for the UI (spinners, bars, logs)
6. **Handles errors** and reports them to the user

---

## 🚦 Usage

### Run the processor
```bash
python earth_engine_processor.py
```

### Options
- Configure download parameters via the frontend or CLI arguments

---

## 📊 Progress & Logs
- Progress is reported to the frontend for live feedback
- All actions are logged in the `logs/` directory
- Errors are reported with user-friendly and technical messages

---

## 🧑‍💻 Developer Tips
- Modular functions for each processing step (easy to extend)
- Threaded downloads for speed and responsiveness
- All errors are caught and logged (no silent failures!)
- Designed for both UI integration and standalone use

---

## 🐞 Error Handling
- User-friendly error messages for the UI
- Detailed logs for debugging
- Graceful recovery from common issues (network, auth, disk)

---

## 🧩 Integration
- Called by the Electron frontend for all download actions
- Can be run standalone for testing and debugging

---

## 📝 Example Workflow
1. User selects AOI and satellite in the UI
2. Processor receives request and starts download
3. Progress bar and logs update in real time
4. Download completes or error is reported

---

## 🤓 For More Info
- See the main backend README for architecture
- Check the code for advanced options and extension points
- Logs are your best friend for troubleshooting!

---

Happy processing! ⚙️🌍 