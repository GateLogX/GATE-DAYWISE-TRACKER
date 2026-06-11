/**
 * FREE WhatsApp Integration for Day-Wise Tracker
 * Connects your existing tracker to Flask backend
 * 100% FREE - uses Twilio trial credit
 */

const BACKEND_URL = 'https://gate-tracker-backend-ct70.onrender.com';

// Sync completed videos to backend
async function syncCompletedVideos(completedVideos) {
    try {
        const lectures = Object.keys(completedVideos).map(messageId => {
            const video = videoData.find(v => v.messageId === messageId);
            if (!video) return null;
            
            return {
                subject: video.subject,
                video_number: parseInt(video.videoNumber),
                message_id: messageId,
                file_name: video.fileName
            };
        }).filter(Boolean);

        if (lectures.length === 0) return;

        const response = await fetch(`${BACKEND_URL}/api/update-progress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                date: new Date().toISOString().split('T')[0],
                completed_lectures: lectures
            })
        });

        if (response.ok) {
            console.log('✅ Synced to backend:', lectures.length, 'lectures');
        }
    } catch (error) {
        console.log('Backend sync failed (offline mode)');
    }
}

// Send daily WhatsApp message (FREE)
async function sendDailyWhatsAppMessage() {
    try {
        const today = daySchedule[selectedDay];
        if (!today) return;

        const remaining = today.videos.filter(v => !completedVideos[v.messageId]);
        
        const message = `📚 GATE 2027 - Day ${selectedDay + 1}
        
Today's Subject: ${today.subject}
Total Videos: ${today.videos.length}
Completed: ${today.videos.length - remaining.length}
Remaining: ${remaining.length}

Keep going! 💪`;

        const response = await fetch(`${BACKEND_URL}/api/test-whatsapp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        if (response.ok) {
            alert('✅ WhatsApp message sent! (FREE via Twilio trial)');
        } else {
            alert('❌ Failed to send. Check if backend is running.');
        }
    } catch (error) {
        alert('❌ Backend not running. Start it first.');
    }
}

// Check backend/WhatsApp status
async function checkWhatsAppStatus() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/health`);
        if (response.ok) {
            return { connected: true, message: '✅ Backend Connected (FREE mode)' };
        }
    } catch (error) {
        return { connected: false, message: '❌ Backend Offline' };
    }
}

// Auto-sync when videos are marked complete
function enableAutoSync() {
    // Save original render function
    const originalRender = window.render;
    
    window.render = function() {
        originalRender();
        
        // Sync to backend after each render
        if (Object.keys(completedVideos).length > 0) {
            syncCompletedVideos(completedVideos);
        }
    };
}

// Add WhatsApp button to UI
function addWhatsAppButton() {
    const headerButtons = document.querySelector('.flex.gap-2');
    if (headerButtons && !document.getElementById('whatsapp-btn')) {
        const btn = document.createElement('button');
        btn.id = 'whatsapp-btn';
        btn.className = 'bg-green-600 text-white px-4 py-2 rounded-full font-bold text-sm hover:bg-green-700';
        btn.innerHTML = '📱 Send WhatsApp Update (FREE)';
        btn.onclick = sendDailyWhatsAppMessage;
        headerButtons.appendChild(btn);
    }
}

// Initialize integration
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 WhatsApp Integration Loaded (100% FREE)');
    enableAutoSync();
    
    // Add WhatsApp button after initial render
    setTimeout(addWhatsAppButton, 500);
    
    // Check status
    checkWhatsAppStatus().then(status => {
        console.log(status.message);
    });
});
