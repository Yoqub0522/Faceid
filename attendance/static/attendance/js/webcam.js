// static/attendance/js/webcam.js (YANGILANGAN - DAVOMAT TUGMASI UCHUN)
let video = null;
let canvas = null;
let context = null;
let stream = null;
let isCameraActive = false;

// 🎥 Kamerani ishga tushurish funksiyasi
function startWebcam() {
    console.log("🔍 startWebcam() funksiyasi chaqirildi");

    video = document.getElementById("video");
    canvas = document.getElementById("canvas");

    if (!video) {
        console.error("❌ Video elementi topilmadi");
        alert("Video elementi topilmadi. Sahifani yangilab ko'ring.");
        return;
    }

    if (!canvas) {
        console.error("❌ Canvas elementi topilmadi");
        return;
    }

    context = canvas.getContext("2d");

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("❌ Brauzeringiz kamera funksiyasini qoʻllab-quvvatlamaydi.");
        return;
    }

    // Oldingi streamni tozalash
    if (stream) {
        stopWebcam();
    }

    // Kamera oqimini olish
    navigator.mediaDevices
        .getUserMedia({
            video: {
                facingMode: "user",
                width: { ideal: 640 },
                height: { ideal: 480 }
            },
            audio: false
        })
        .then((mediaStream) => {
            console.log("✅ Kamera ruhsat berildi");
            stream = mediaStream;
            video.srcObject = mediaStream;
            isCameraActive = true;

            // Video yuklanganda
            video.onloadedmetadata = () => {
                console.log("✅ Kamera muvaffaqiyatli ishga tushdi");

                // Canvas o'lchamlarini video ga moslashtirish
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                // Status yangilash
                updateStatus();
            };

            video.play().catch(err => {
                console.error("❌ Video play error:", err);
                alert("Kamerani ishga tushirishda xatolik: " + err.message);
            });

        })
        .catch((err) => {
            console.error("❌ Camera error:", err);
            isCameraActive = false;
            updateStatus();

            let errorMessage = "Kamera ochishda xatolik: ";
            switch (err.name) {
                case 'NotAllowedError':
                    errorMessage += "Kamera ruxsati berilmagan. Iltimos, brauzer sozlamalaridan ruxsat bering.";
                    break;
                case 'NotFoundError':
                    errorMessage += "Kamera topilmadi. Kamera ulanganligiga ishonch hosil qiling.";
                    break;
                case 'NotSupportedError':
                    errorMessage += "Bu brauzer kamera funksiyasini qo'llab-quvvatlamaydi.";
                    break;
                default:
                    errorMessage += err.message;
            }

            alert(errorMessage);
        });
}

// 🖼️ Suratni olish va base64 formatga o'tkazish
function captureToBase64() {
    console.log("🔍 captureToBase64() funksiyasi chaqirildi");

    if (!video || !video.srcObject) {
        console.error("❌ Video yoki video stream mavjud emas");
        alert("❌ Kamera hali tayyor emas yoki faol emas. Avval kamerni yoqing.");
        return null;
    }

    if (!context) {
        console.error("❌ Context mavjud emas");
        context = canvas.getContext("2d");
    }

    try {
        // Canvas o'lchamlarini yangilash
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Canvas ga video frame ni chizish
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Sifat sozlamalari
        const quality = 0.8; // 80% sifat
        const imageData = canvas.toDataURL("image/jpeg", quality);

        console.log("📸 Surat olindi, hajmi:", Math.round((imageData.length * 0.75) / 1024), "KB");
        return imageData;

    } catch (err) {
        console.error("❌ Surat olishda xatolik:", err);
        alert("Suratni olishda xatolik: " + err.message);
        return null;
    }
}

// 📤 Suratni serverga yuborish - ASOSIY FUNKSIYA
async function captureAndSend() {
    console.log("🔍 captureAndSend() funksiyasi chaqirildi");

    // Kamera holatini tekshirish
    if (!isCameraActive || !video || !video.srcObject) {
        alert("❌ Kamera faol emas. Iltimos, avval 'Kamerni Yoqish' tugmasini bosing.");
        return;
    }

    const resultDiv = document.getElementById('result');
    if (resultDiv) {
        resultDiv.innerHTML = '<p>⏳ Surat olinmoqda...</p>';
    }

    // Suratni olish
    const imageData = captureToBase64();

    if (!imageData) {
        console.error("❌ Surat olish muvaffaqiyatsiz");
        if (resultDiv) {
            resultDiv.innerHTML = '<p style="color: red;">❌ Surat olish muvaffaqiyatsiz</p>';
        }
        return;
    }

    console.log("🌐 Serverga so'rov yuborilmoqda...");

    if (resultDiv) {
        resultDiv.innerHTML = '<p>⏳ Yuzni tanish jarayonda...</p>';
    }

    try {
        // Serverga so'rov yuborish
        const response = await fetch('/process_attendance/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `image=${encodeURIComponent(imageData)}`
        });

        console.log("✅ Server javobi qabul qilindi, status:", response.status);

        if (!response.ok) {
            throw new Error(`Server xatosi: ${response.status}`);
        }

        const data = await response.json();
        console.log("📊 Server javobi:", data);

        if (resultDiv) {
            if (data.status === 'success') {
                resultDiv.innerHTML = `
                    <div style="color: green; font-weight: bold; font-size: 18px;">
                        ✅ ${data.action || 'Davomat qilindi'}
                    </div>
                    <div style="font-size: 16px; margin: 10px 0;">
                        Xodim: <strong>${data.employee_name}</strong>
                    </div>
                    <div style="font-size: 14px; color: #666;">
                        Masofa: ${data.distance} | Vaqt: ${data.processing_time}s
                    </div>
                `;
            } else if (data.status === 'no_match') {
                resultDiv.innerHTML = `
                    <div style="color: orange; font-weight: bold; font-size: 18px;">
                        ❌ ${data.message || 'Tanishmadi'}
                    </div>
                    <div style="font-size: 14px; color: #666; margin-top: 10px;">
                        Eng yaqin masofa: ${data.min_distance} (chegara: ${data.threshold})
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `
                    <div style="color: red; font-weight: bold;">
                        ❌ ${data.message || 'Xatolik yuz berdi'}
                    </div>
                `;
            }
        }

    } catch (error) {
        console.error('❌ Server xatosi:', error);
        if (resultDiv) {
            resultDiv.innerHTML = `
                <div style="color: red; font-weight: bold;">
                    ❌ Server bilan aloqa xatosi
                </div>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">
                    ${error.message}
                </div>
            `;
        }
    }
}

// 🛑 Kamerani to'xtatish
function stopWebcam() {
    console.log("🔍 stopWebcam() funksiyasi chaqirildi");

    if (stream) {
        let tracks = stream.getTracks();
        tracks.forEach((track) => {
            track.stop();
            console.log("📹 Kamera track to'xtatildi:", track.kind);
        });
        stream = null;
    }

    if (video) {
        video.srcObject = null;
    }

    isCameraActive = false;
    updateStatus();
    console.log("🛑 Kamera to'xtatildi");
}

// 📊 Kamera holatini yangilash
function updateStatus() {
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        if (isCameraActive) {
            statusDiv.innerHTML = '🟢 Kamera faol - "Davomat Qilish" tugmasini bosing';
            statusDiv.className = 'status status-active';
        } else {
            statusDiv.innerHTML = '🔴 Kamera faol emas - "Kamerni Yoqish" tugmasini bosing';
            statusDiv.className = 'status status-inactive';
        }
    }
}

// 🔄 Kamerani qayta ishga tushirish
function restartWebcam() {
    console.log("🔍 restartWebcam() funksiyasi chaqirildi");
    stopWebcam();
    setTimeout(startWebcam, 500);
}

// Global qilib e'lon qilamiz
window.startWebcam = startWebcam;
window.captureToBase64 = captureToBase64;
window.stopWebcam = stopWebcam;
window.restartWebcam = restartWebcam;
window.captureAndSend = captureAndSend;
window.isCameraActive = isCameraActive;

console.log("✅ webcam.js yuklandi - barcha funksiyalar mavjud");