# Two phones at once

Some behaviour only exists between two devices: a call, a chat message arriving, a shared list updating. Drive both from one script on the Mac: the iPhone through the runner, the Android through adb. Then judge the result from both phones' trails plus the server's log, not from one screen.

## Keeping them in step

- **One clock.** Both phones and the Mac keep NTP time. The runner's `at:<ms since 1970>` step waits until that moment, so the script can say "the iPhone taps answer at T, the Android hangs up at T+2 s".
- **React to lines as they come.** The runner flushes every line (`setvbuf` in Steps.swift), so the script can read `xcodebuild`'s output as a stream, wait for `OK tap:call-start`, and then act on the Android.
- **Name everything by wall-clock time.** Recordings and contact sheets carry it (`sheets.mjs`), so "what did each phone show at 14:02:07.3" is a lookup.

## One scenario, one folder

Keep per scenario: both trails, the server's events for that window (slice the log from a byte offset taken at the start), the runner's screenshots and recording, the Android recording and the app's own logcat, crash reports from both phones (see ios-runner.md and android.md), and the contact sheets.

## The judge

Write the pass/fail rules down in the script, so a scenario is judged the same way every time. For example, fail when:

- the server's outcome is wrong, or a phone disagrees with it (shows connected, but the server never connected it);
- either screen shows an error line, or either phone isn't back where it should be at the end;
- either app crashed (the Android crash buffer, an iPhone `.ips` newer than the start);
- a privacy rule broke (the Android's mic `running` while it only rings: sample `appops` each second).

Warn, without failing, on slow API calls and slow connects.

Run each scenario in both directions (the iPhone starts it, then the Android starts it). Bugs hide in one direction.
