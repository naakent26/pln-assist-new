import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../common.dart';
import '../../models/user_model.dart';

/// Guard that hides widgets based on the current user's role.
///
/// Example:
/// ```dart
/// RoleGuard(
///   minRole: Role.spv,
///   child: IconButton(icon: Icon(Icons.admin_panel_settings), onPressed: () {}),
/// )
/// ```
class RoleGuard extends StatelessWidget {
  final Role minRole;
  final Widget child;
  final Widget? fallback;

  const RoleGuard({
    super.key,
    required this.minRole,
    required this.child,
    this.fallback,
  });

  bool _canAccess(UserModel user) {
    final currentRole = Role.values.firstWhere(
      (role) => role.name == user.role.value.toLowerCase(),
      orElse: () => Role.umum,
    );
    return currentRole.value >= minRole.value;
  }

  @override
  Widget build(BuildContext context) {
    // UserModel is a plain global (gFFI.userModel), not a GetX-registered
    // service, so it must not be looked up via Get.find.
    final user = gFFI.userModel;
    return Obx(
      () => _canAccess(user) ? child : fallback ?? const SizedBox.shrink(),
    );
  }
}

enum Role { umum, biller, pbm, spv, admin }

extension RoleCompare on Role {
  int get value {
    switch (this) {
      case Role.umum:
        return 0;
      case Role.biller:
        return 1;
      case Role.pbm:
        return 2;
      case Role.spv:
        return 3;
      case Role.admin:
        return 4;
    }
  }

  String get label {
    switch (this) {
      case Role.umum:
        return 'Umum';
      case Role.biller:
        return 'Biller';
      case Role.pbm:
        return 'PBM';
      case Role.spv:
        return 'SPV';
      case Role.admin:
        return 'Admin';
    }
  }
}
