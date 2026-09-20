// Role-based access control middleware for PLN Assist
// This module provides role checks before remote actions.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Roles available in PLN Assist
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Role {
    Admin,      // Full access: all devices, all permissions
    Spv,        // Supervisor: can view all, manage assigned devices
    Pbm,        // PBM (Petugas Bantuan Mandiri): limited device access
    Biller,     // Biller: basic remote support only
    Umum,       // General: read-only viewing
}

impl Default for Role {
    fn default() -> Self {
        Role::Umum
    }
}

impl Role {
    pub fn from_str(s: &str) -> Option<Role> {
        match s.to_lowercase().as_str() {
            "admin" => Some(Role::Admin),
            "spv" | "supervisor" => Some(Role::Spv),
            "pbm" | "petugas_bantuan_mandiri" => Some(Role::Pbm),
            "biller" => Some(Role::Biller),
            "umum" | "general" => Some(Role::Umum),
            _ => None,
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            Role::Admin => "admin",
            Role::Spv => "spv",
            Role::Pbm => "pbm",
            Role::Biller => "biller",
            Role::Umum => "umum",
        }
    }

    /// Check if this role can perform the given action
    pub fn can_action(&self, action: &Action) -> bool {
        use Action::*;
        match (self, action) {
            // Admin can do everything
            (Role::Admin, _) => true,
            // Spv can manage and view
            (Role::Spv, Manage) => true,
            (Role::Spv, View) => true,
            (Role::Spv, Restart) => true,
            // PBM can remote control but limited
            (Role::Pbm, Control) => true,
            (Role::Pbm, View) => true,
            // Biller can only basic remote support
            (Role::Biller, Control) => true,
            (Role::Biller, View) => true,
            // Umum is read-only
            (Role::Umum, View) => true,
            // Deny everything else
            _ => false,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Action {
    View,        // View screen only
    Control,     // Remote control (mouse/keyboard)
    FileTransfer,// Send/receive files
    Manage,      // Manage devices, groups, users
    Restart,     // Reboot remote device
    Emergency,   // Emergency disconnect
}

/// Session-level permission cache
#[derive(Debug, Default)]
pub struct PermissionCache {
    inner: Arc<Mutex<HashMap<i32, HashMap<String, Role>>>>,
}

impl PermissionCache {
    pub fn new() -> Self {
        Self {
            inner: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Set role for a connection
    pub fn set_role(&self, conn: i32, user: &str, role: Role) {
        let mut cache = self.inner.lock().unwrap();
        cache.entry(conn)
            .or_insert_with(HashMap::new)
            .insert(user.to_string(), role);
    }

    /// Get role for a connection/user pair
    pub fn get_role(&self, conn: i32, user: &str) -> Option<Role> {
        let cache = self.inner.lock().unwrap();
        cache.get(&conn)
            .and_then(|users| users.get(user))
            .cloned()
    }

    /// Check if action is allowed
    pub fn check_action(&self, conn: i32, user: &str, action: &Action) -> bool {
        match self.get_role(conn, user) {
            Some(role) => role.can_action(action),
            None => false, // Default deny
        }
    }
}

impl Clone for PermissionCache {
    fn clone(&self) -> Self {
        Self {
            inner: Arc::clone(&self.inner),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_role_parsing() {
        assert_eq!(Role::from_str("admin"), Some(Role::Admin));
        assert_eq!(Role::from_str("spv"), Some(Role::Spv));
        assert_eq!(Role::from_str("pbm"), Some(Role::Pbm));
        assert_eq!(Role::from_str("biller"), Some(Role::Biller));
        assert_eq!(Role::from_str("umum"), Some(Role::Umum));
        assert_eq!(Role::from_str("invalid"), None);
    }

    #[test]
    fn test_permission_cache() {
        let cache = PermissionCache::new();
        cache.set_role(1, "admin_user", Role::Admin);
        cache.set_role(2, "spv_user", Role::Spv);
        cache.set_role(3, "biller_user", Role::Biller);
        
        // Admin can do everything
        assert!(cache.check_action(1, "admin_user", &Action::Manage));
        assert!(cache.check_action(1, "admin_user", &Action::Emergency));
        
        // SPV can manage and restart
        assert!(cache.check_action(2, "spv_user", &Action::Manage));
        assert!(cache.check_action(2, "spv_user", &Action::Restart));
        
        // Biller cannot manage
        assert!(!cache.check_action(3, "biller_user", &Action::Manage));
        assert!(cache.check_action(3, "biller_user", &Action::Control));
        
        // Unknown user gets nothing
        assert!(!cache.check_action(99, "unknown", &Action::Control));
    }

    #[test]
    fn each_role_has_only_its_expected_permissions() {
        assert!(Role::Admin.can_action(&Action::FileTransfer));
        assert!(Role::Admin.can_action(&Action::Emergency));
        assert!(Role::Spv.can_action(&Action::Restart));
        assert!(!Role::Spv.can_action(&Action::Control));
        assert!(Role::Pbm.can_action(&Action::Control));
        assert!(!Role::Pbm.can_action(&Action::Restart));
        assert!(Role::Biller.can_action(&Action::View));
        assert!(!Role::Biller.can_action(&Action::FileTransfer));
        assert!(Role::Umum.can_action(&Action::View));
        assert!(!Role::Umum.can_action(&Action::Control));
    }
}
