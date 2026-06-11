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

// Load completed videos FROM backend
async function loadCompletedFromBackend() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/progress`);
        if (!response.ok) {
            console.log('⏳ Backend deploying... Completed lectures will sync on next refresh');
            return;
        }
        
        const data = await response.json();
        if (!data.success || !data.completed_lectures) {
            console.log('No completed lectures from backend');
            return;
        }
        
        // CLEAR localStorage first - backend is source of truth
        completedVideos = {};
        
        // Mark videos as completed in the UI from backend
        let syncedCount = 0;
        data.completed_lectures.forEach(lecture => {
            // Find matching video in videoData
            const video = videoData.find(v => 
                v.subject === lecture.subject && 
                parseInt(v.videoNumber) === lecture.video_number
            );
            
            if (video) {
                completedVideos[video.messageId] = true;
                syncedCount++;
            }
        });
        
        // Save to localStorage and re-render
        localStorage.setItem('completedVideos', JSON.stringify(completedVideos));
        if (window.render) {
            window.render();
        }
        
        console.log(`✅ Loaded ${syncedCount} lectures from backend (cleared local cache)`);
    } catch (error) {
        console.log('⏳ Could not reach backend. Will retry on next page load.');
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

// Load timetable from backend
async function loadTimetableFromBackend() {
    try {
        console.log('📅 Loading timetable from backend...');
        
        // Fetch complete timetable from new endpoint
        const response = await fetch(`${BACKEND_URL}/api/full-timetable`);
        if (!response.ok) {
            console.log('⚠️ Could not load timetable from backend, using local CSV data');
            return false;
        }
        
        const data = await response.json();
        
        // ALWAYS use backend timetable if available (it's the source of truth)
        if (data.success && data.timetable && Array.isArray(data.timetable) && data.timetable.length > 0) {
            // Backend timetable has the videos already embedded, use it directly
            window.daySchedule = data.timetable;
            window.backlogDays = data.timetable.map(day => ({ ...day, completed: false }));
            
            // Also populate videoData from the backend timetable
            window.videoData = [];
            data.timetable.forEach(day => {
                if (day.videos && Array.isArray(day.videos)) {
                    day.videos.forEach(video => {
                        window.videoData.push({
                            subject: video.subject,
                            videoNumber: video.videoNumber,
                            fileName: video.fileName,
                            durationSeconds: video.durationSeconds,
                            messageId: video.messageId
                        });
                    });
                }
            });
            
            console.log(`✅ Loaded ${data.timetable.length} days from backend (${data.goals?.daily_study_hours || '?'} hrs/day)`);
            console.log(`📹 Loaded ${window.videoData.length} videos from backend timetable`);
            
            // Re-render UI with new timetable
            if (window.render) {
                window.render();
            }
            return true;
        } else {
            console.log('⚠️ Backend timetable is empty, keeping local CSV data');
            return false;
        }
    } catch (error) {
        console.log('⚠️ Timetable load failed:', error.message);
        return false;
    }
}

// Initialize integration - Wait for CSV then override with backend
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 WhatsApp Integration Loaded (100% FREE)');
    
    // Wait 2 seconds for CSV to populate videoData
    setTimeout(() => {
        console.log('🔄 Now loading backend timetable to override schedule...');
        
        // Load backend timetable (it will populate both daySchedule and videoData)
        loadTimetableFromBackend().then((loaded) => {
            if (loaded) {
                console.log('✅ Using backend timetable (120 days, 4hrs/day)');
            } else {
                console.log('⚠️ Backend failed, using CSV schedule');
            }
            
            // Then load completed videos
            return loadCompletedFromBackend();
        }).then(() => {
            enableAutoSync();
            
            // Add WhatsApp button
            setTimeout(addWhatsAppButton, 500);
            
            // Check status
            checkWhatsAppStatus().then(status => {
                console.log(status.message);
            });
        });
    }, 2000); // Wait 2 seconds for CSV to finish loading
});
