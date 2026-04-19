// static/js/main.js
// Purpose : Client-side logic — camera access, fetch() API calls to Flask,
//           and DOM updates for all interactive pages.
//
// Sections to implement:
//   1. startCamera(videoElementId)
//      Opens the user's webcam and streams it into a <video> element.
//
//   2. captureFrame(videoElement)
//      Draws one frame onto a hidden <canvas> and returns it as a base64 PNG.
//
//   3. registerStudent(formData)
//      POST /register — sends student info + face image to backend.
//
//   4. startAttendance(sessionId)
//      Continuously captures frames and POST /recognize every ~2 seconds.
//      Displays recognised student name and marks attendance.
//
//   5. loadAttendance(filters)
//      GET /attendance — fetches records and populates the dashboard table.
//
//   6. exportCSV()
//      Triggers GET /export which returns a downloadable CSV file.
//
// TODO: implement each function above
// TODO: handle fetch() errors gracefully (show user-friendly messages)
// TODO: stop the camera stream when the user navigates away
