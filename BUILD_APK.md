# Build APK Instructions

Since Android SDK/Gradle is not available on this system, here's the simplest way to get your APK:

## Option 1: Use Android Studio (Fastest)
1. Open the `android` folder in Android Studio
2. Wait for Gradle sync to complete
3. Click **Build > Build Bundle(s) / APK(s) > Build APK(s)**
4. APK will be at: `android\app\build\outputs\apk\debug\app-debug.apk`

## Option 2: Serve the APK via localhost
After building (using Option 1):

1. Open PowerShell in the APK directory:
```powershell
cd "D:\Deeni Maslah\android\app\build\outputs\apk\debug"
python -m http.server 8001
```

2. Find your PC's IP address:
```powershell
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.50)

3. On your phone (same Wi-Fi), open browser and go to:
```
http://192.168.1.50:8001/app-debug.apk
```

4. Download and install (you may need to enable "Install from unknown sources")

## Configure the App
After installing:
- Open the app
- Set Base URL to: `http://192.168.1.50:8000/` (use your PC's IP)
- Tap "Save Base URL"
- Select language (Urdu/English)
- Ask your question

## Backend Server
Make sure the backend is running:
```powershell
cd "D:\Deeni Maslah"
& "D:/Deeni Maslah/.venv/Scripts/python.exe" -m uvicorn app:app --host 0.0.0.0 --port 8000
```
Note: Use `--host 0.0.0.0` so your phone can reach it!
