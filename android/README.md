# Deeni Q&A Android App

A native Android (Kotlin) app that calls the FastAPI backend to answer questions strictly from the Urdu book Taleem-ul-Islam.

## Backend URL
- Emulator: use `http://10.0.2.2:8000/`
- Physical device: use your PC's LAN IP, e.g., `http://192.168.1.50:8000/`
- Set in the app via the Base URL field and tap "Save Base URL".

## Build & Run (Android Studio)
1. Open folder `android/` in Android Studio.
2. Let Gradle sync; if asked to update Android Gradle Plugin/Kotlin, accept.
3. Run the app on the emulator or a device.

## UI
- Language toggle: Urdu / English.
- Question input.
- Ask button.
- Answer and source display.
- Disclaimer: Answers derived only from Taleem-ul-Islam.

## API
POST /ask
Body:
```
{ "question": "string", "language": "urdu|english" }
```
Response:
```
{ "answer": "string", "source": "chapter/page if available" }
```

## Notes
- Ensure the backend is running and reachable from the phone.
- First backend run builds FAISS index and downloads models; allow time.
- The app does not store data; it only sends questions and displays answers.
