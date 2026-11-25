//! How Rust declares functions from a C library, here two from the NDI® SDK.
//! Declarations only: this example never links to NDI or calls them.

use std::ffi::{c_char, c_void};

/// Must match the C struct byte for byte, so `repr(C)` turns off Rust's own field ordering.
#[repr(C)]
pub struct NdiSendCreate {
    pub p_ndi_name: *const c_char,
    pub p_groups: *const c_char,
    pub clock_video: bool,
    pub clock_audio: bool,
}

unsafe extern "C" {
    pub fn NDIlib_initialize() -> bool;
    pub fn NDIlib_send_create(settings: *const NdiSendCreate) -> *mut c_void;
}
