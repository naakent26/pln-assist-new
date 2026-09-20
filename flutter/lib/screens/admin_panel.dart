import 'package:flutter/material.dart';
import 'package:flutter_hbb/common.dart';
import 'package:flutter_hbb/common/widgets/role_guard.dart';
import 'package:flutter_hbb/models/audit_model.dart';
import 'package:flutter_hbb/models/user_model.dart';

/// Admin panel: current signed-in operator, their role and what that role may do.
///
/// Opened from the home pane for SPV/Admin only. Role changes come from the
/// server (`role` in the login payload); this panel only reflects them.
class AdminPanel extends StatelessWidget {
  const AdminPanel({super.key});

  @override
  Widget build(BuildContext context) {
    final user = gFFI.userModel;
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _userCard(user),
          const SizedBox(height: 16),
          Text('Hak akses per role',
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          ...Role.values.reversed.map(_roleRow),
        ],
      ),
    );
  }

  Widget _userCard(UserModel user) {
    return Obx(() {
      final name = user.displayNameOrUserName.trim();
      final role = Role.values.firstWhere(
        (r) => r.name == user.role.value.toLowerCase(),
        orElse: () => Role.umum,
      );
      return Card(
        child: ListTile(
          leading: CircleAvatar(
            child: Text(name.isEmpty ? '?' : name[0].toUpperCase()),
          ),
          title: Text(name.isEmpty ? 'Belum login' : name),
          subtitle: Text('Role: ${role.label}'),
          trailing: const Icon(Icons.admin_panel_settings),
        ),
      );
    });
  }

  Widget _roleRow(Role role) {
    return ListTile(
      dense: true,
      contentPadding: EdgeInsets.zero,
      leading: CircleAvatar(
        radius: 14,
        backgroundColor: _roleColor(role),
        child: const Icon(Icons.person, size: 14, color: Colors.white),
      ),
      title: Text(role.label),
      subtitle: Text(_roleScope(role)),
    );
  }

  String _roleScope(Role role) {
    switch (role) {
      case Role.admin:
        return 'Semua perangkat, role, policy, update, audit, emergency revoke';
      case Role.spv:
        return 'Perangkat dan sesi dalam area tanggung jawab, audit area';
      case Role.pbm:
        return 'Remote perangkat dalam group yang ditugaskan';
      case Role.biller:
        return 'Remote perangkat billing yang ditugaskan';
      case Role.umum:
        return 'Perangkat sendiri, menyetujui sesi, emergency disconnect';
    }
  }

  Color _roleColor(Role role) {
    switch (role) {
      case Role.admin:
        return Colors.red.shade700;
      case Role.spv:
        return Colors.blue.shade700;
      case Role.pbm:
        return Colors.green.shade700;
      case Role.biller:
        return Colors.orange.shade700;
      case Role.umum:
        return Colors.grey.shade700;
    }
  }
}

/// Opens the admin panel and records the access in the audit trail.
Future<void> showAdminPanel(BuildContext context) async {
  AuditLogger.log(AuditEntry(
    timestamp: DateTime.now(),
    eventType: 'admin_panel_open',
    userId: gFFI.userModel.displayNameOrUserName,
    details: 'Role ${gFFI.userModel.role.value}',
  ));
  if (!context.mounted) return;
  await showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: const Text('Admin Panel'),
      content: const SizedBox(width: 420, child: AdminPanel()),
      actions: [
        TextButton(
          onPressed: () {
            AuditLogger.log(AuditEntry(
              timestamp: DateTime.now(),
              eventType: 'admin_panel_close',
              userId: gFFI.userModel.displayNameOrUserName,
            ));
            Navigator.of(ctx).pop();
          },
          child: const Text('Tutup'),
        ),
      ],
    ),
  );
}
