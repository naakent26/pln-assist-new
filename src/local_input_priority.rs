use std::sync::{Mutex, OnceLock};
use std::time::{Duration, Instant};

pub const LOCAL_INPUT_GRACE_PERIOD: Duration = Duration::from_secs(5);

fn latest_local_input() -> &'static Mutex<Option<Instant>> {
    static LATEST_LOCAL_INPUT: OnceLock<Mutex<Option<Instant>>> = OnceLock::new();
    LATEST_LOCAL_INPUT.get_or_init(|| Mutex::new(None))
}

pub fn record_local_input() {
    *latest_local_input().lock().unwrap() = Some(Instant::now());
}

pub fn remote_input_allowed() -> bool {
    latest_local_input()
        .lock()
        .unwrap()
        .map(|at| at.elapsed() >= LOCAL_INPUT_GRACE_PERIOD)
        .unwrap_or(true)
}

#[cfg(windows)]
mod windows {
    use super::record_local_input;
    use std::cell::RefCell;
    use std::os::raw::c_int;
    use std::ptr::null_mut;
    use winapi::shared::{minwindef::*, windef::HHOOK};
    use winapi::um::winuser::*;

    thread_local! {
        static MOUSE_HOOK: RefCell<HHOOK> = RefCell::new(null_mut());
        static KEYBOARD_HOOK: RefCell<HHOOK> = RefCell::new(null_mut());
    }

    extern "system" fn mouse_hook(code: c_int, wparam: WPARAM, lparam: LPARAM) -> LRESULT {
        if code == HC_ACTION
            && matches!(
                wparam as UINT,
                WM_MOUSEMOVE | WM_LBUTTONDOWN | WM_LBUTTONUP | WM_RBUTTONDOWN | WM_RBUTTONUP
                    | WM_MBUTTONDOWN | WM_MBUTTONUP | WM_MOUSEWHEEL | WM_MOUSEHWHEEL
                    | WM_XBUTTONDOWN | WM_XBUTTONUP
            )
        {
            let input = unsafe { &*(lparam as *const MSLLHOOKSTRUCT) };
            if input.flags & LLMHF_INJECTED == 0 {
                record_local_input();
            }
        }
        unsafe { CallNextHookEx(null_mut() as HHOOK, code, wparam, lparam) }
    }

    extern "system" fn keyboard_hook(code: c_int, wparam: WPARAM, lparam: LPARAM) -> LRESULT {
        if code == HC_ACTION
            && matches!(wparam as UINT, WM_KEYDOWN | WM_KEYUP | WM_SYSKEYDOWN | WM_SYSKEYUP)
        {
            let input = unsafe { &*(lparam as *const KBDLLHOOKSTRUCT) };
            if input.flags & LLKHF_INJECTED == 0 {
                record_local_input();
            }
        }
        unsafe { CallNextHookEx(null_mut() as HHOOK, code, wparam, lparam) }
    }

    pub fn start() {
        unsafe {
            let mouse = SetWindowsHookExW(WH_MOUSE_LL, Some(mouse_hook), null_mut(), 0);
            MOUSE_HOOK.with(|h| *h.borrow_mut() = mouse);
            let keyboard = SetWindowsHookExW(WH_KEYBOARD_LL, Some(keyboard_hook), null_mut(), 0);
            KEYBOARD_HOOK.with(|h| *h.borrow_mut() = keyboard);
            if mouse.is_null() || keyboard.is_null() {
                hbb_common::log::warn!("PLN Assist local input priority hook could not start");
            }
        }
    }
}

#[cfg(windows)]
pub fn start() {
    use std::sync::Once;
    use std::thread;

    static START: Once = Once::new();
    START.call_once(|| {
        thread::spawn(|| unsafe {
            let mut message: winapi::um::winuser::MSG = std::mem::zeroed();
            windows::start();
            while winapi::um::winuser::GetMessageW(&mut message, std::ptr::null_mut(), 0, 0) > 0 {}
        });
    });
}

#[cfg(not(windows))]
pub fn start() {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn local_input_blocks_remote_input_for_five_seconds() {
        record_local_input();
        assert!(!remote_input_allowed());
    }
}
