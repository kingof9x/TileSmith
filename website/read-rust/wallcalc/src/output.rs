//! Sending frames to an output on its own thread, the way a video sender works.

use std::sync::mpsc;
use std::sync::{Arc, Mutex};
use std::thread;

/// One picture of the wall, as raw RGBA bytes.
pub struct Frame {
    pub number: u64,
    pub pixels: Vec<u8>,
}

/// Sends `count` frames to a worker thread and returns how many it handled.
pub fn run_sender(count: u64) -> u64 {
    let handled = Arc::new(Mutex::new(0u64)); // a counter both threads can reach
    let (tx, rx) = mpsc::channel::<Frame>(); // a pipe: tx is the write end, rx the read end

    let counter = Arc::clone(&handled);
    let worker = thread::spawn(move || {
        for frame in rx {
            // a real sender would pass frame.pixels to the video library here
            let _bytes = frame.pixels.len();
            *counter.lock().unwrap() += 1;
        }
        // the loop ends when every tx has been dropped (the pipe is closed)
    });

    for number in 0..count {
        let frame = Frame {
            number,
            pixels: vec![0; 4 * 192 * 192],
        };
        tx.send(frame).expect("the sender thread has stopped");
    }
    drop(tx); // close the pipe so the worker's loop ends
    worker.join().expect("the sender thread crashed");

    *handled.lock().unwrap()
}

#[cfg(test)]
mod tests {
    #[test]
    fn every_frame_is_handled() {
        assert_eq!(super::run_sender(5), 5);
    }
}
