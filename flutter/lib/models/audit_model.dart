// Session recording utility for audit trail
// Records screen sessions to local file, uploads to R2 on disconnect

import 'dart:async';

/// Configuration for session recording
class RecordingConfig {
  final String outputDir;
  final int maxDurationMinutes;
  final String recordingFormat; // 'mp4', 'mkv', 'webm'

  const RecordingConfig({
    this.outputDir = '/tmp/plnassist_recordings',
    this.maxDurationMinutes = 60,
    this.recordingFormat = 'mp4',
  });
}

/// Audit log entry - captures every significant event
class AuditEntry {
  final DateTime timestamp;
  final String eventType; // login, logout, reconnect, restart, emergency_disconnect
  final String userId;
  final String? targetDeviceId;
  final String? details;

  AuditEntry({
    required this.timestamp,
    required this.eventType,
    required this.userId,
    this.targetDeviceId,
    this.details,
  });

  Map<String, dynamic> toJson() => {
        'timestamp': timestamp.toUtc().toIso8601String(),
        'event_type': eventType,
        'user_id': userId,
        'target_device_id': targetDeviceId,
        'details': details,
      };
}

/// In-memory audit logger (will be persisted to D1 later)
class AuditLogger {
  static final List<AuditEntry> _entries = [];
  static final StreamController<AuditEntry> _onNewEntry =
      StreamController.broadcast();

  static List<AuditEntry> get entries => List.unmodifiable(_entries);
  static Stream<AuditEntry> get onNewEntry => _onNewEntry.stream;

  static void log(AuditEntry entry) {
    _entries.add(entry);
    _onNewEntry.add(entry);
    // TODO: Persist to D1/database
    // Future.microtask(() => _persistToDatabase(entry));
  }

  static Future<void> _persistToDatabase(AuditEntry entry) async {
    // Insert into D1 with: INSERT INTO audit_logs VALUES (?, ?, ?, ?, ?)
    // This will be implemented when server is ready
  }

  static void clear() => _entries.clear();
}

/// Emergency disconnect handler
class EmergencyDisconnect {
  /// Revoke all sessions for a user (admin action)
  static Future<bool> revokeAllSessions(String userId) async {
    // TODO: Call server API to revoke sessions
    // POST /api/sessions/revoke
    // Body: { user_id: userId }
    AuditLogger.log(AuditEntry(
      timestamp: DateTime.now(),
      eventType: 'emergency_revoke',
      userId: userId,
      details: 'All sessions revoked by admin',
    ));
    return true;
  }

  /// Disconnect specific peer
  static Future<bool> disconnectPeer(String peerId, String userId) async {
    // TODO: Send close_reason message to peer
    // peer.send_message(Message { close_reason: "Disconnected by admin" })
    AuditLogger.log(AuditEntry(
      timestamp: DateTime.now(),
      eventType: 'emergency_disconnect',
      userId: userId,
      targetDeviceId: peerId,
      details: 'Peer disconnected by admin',
    ));
    return true;
  }
}
