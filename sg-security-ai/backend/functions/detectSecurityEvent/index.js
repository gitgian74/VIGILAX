const sdk = require('node-appwrite');

module.exports = async function (req, res) {
  const client = new sdk.Client();
  const database = new sdk.Databases(client);

  client
    .setEndpoint(req.variables['APPWRITE_ENDPOINT'])
    .setProject(req.variables['APPWRITE_PROJECT_ID'])
    .setKey(req.variables['APPWRITE_API_KEY']);

  try {
    const payload = JSON.parse(req.payload);
    const { frame, cameraName, timestamp, zones } = payload;

    // Qui andrebbe la logica di ML per detection
    // Per ora simuliamo una detection
    const detections = await analyzeFrame(frame, zones);

    if (detections.length > 0) {
      // Salva eventi nel database
      for (const detection of detections) {
        await database.createDocument(
          req.variables['DATABASE_ID'],
          'security_events',
          'unique()',
          {
            type: detection.type,
            timestamp: new Date(timestamp),
            cameraName,
            zone: detection.zone,
            confidence: detection.confidence,
            details: JSON.stringify(detection.details),
            severity: calculateSeverity(detection),
            processed: false,
            notificationsSent: false
          }
        );
      }
    }

    res.json({ success: true, detections });
  } catch (error) {
    console.error('Error:', error);
    res.json({ success: false, error: error.message }, 500);
  }
};

async function analyzeFrame(frame, zones) {
  // Placeholder per logica ML
  // In produzione, qui si userebbe un modello TensorFlow o simile
  return [];
}

function calculateSeverity(detection) {
  if (detection.type === 'intrusion') return 'critical';
  if (detection.confidence > 0.9) return 'high';
  if (detection.confidence > 0.7) return 'medium';
  return 'low';
}
