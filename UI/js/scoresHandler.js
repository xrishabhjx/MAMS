const fs = require('fs');
const path = require('path');

const scoresFilePath = path.join(__dirname, 'scores.json');

let faceScore = null;
let audioScore = null;

// Save face score
function saveFaceScore(score) {
    console.log(`Received face score: ${score}`);
    faceScore = score;
    checkAndSaveScores();
}

// Save audio score
function saveAudioScore(score) {
    console.log(`Received audio score: ${score}`);
    audioScore = score;
    checkAndSaveScores();
}

// Check if both scores are present, then save to file
function checkAndSaveScores() {
    if (faceScore !== null && audioScore !== null) {
        const data = {
            faceScore,
            audioScore,
            timestamp: new Date().toISOString()
        };
        fs.writeFile(scoresFilePath, JSON.stringify(data, null, 2), (err) => {
            if (err) {
                console.error('Error writing scores file:', err);
            } else {
                console.log('Scores saved successfully:', data);
                // Optionally, trigger attendance marking here
            }
        });

        // Reset scores after saving
        faceScore = null;
        audioScore = null;
    }
}

module.exports = {
    saveFaceScore,
    saveAudioScore,
};
