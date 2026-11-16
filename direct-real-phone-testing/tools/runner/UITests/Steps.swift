import ObjectiveC
import XCTest

// Walks journeys through the installed app on the real iPhone. The app is chosen by
// TEST_RUNNER_APP_BUNDLE_ID (XCTest sees it as APP_BUNDLE_ID); the steps come from
// TEST_RUNNER_STEPS, "|"-separated. Elements are found by testID (accessibility identifier)
// or by label.
//
//   journey:name         starts a journey; after a FAIL the rest of that journey is skipped
//   tap:id               tap the element with that testID (once its frame stops moving)
//   label:text / has:text   tap the element whose label is / contains text
//   expect:id            wait until it exists (fails the journey if not), prints how long
//   either:id1/id2       wait until one of them exists, prints which
//   see:text             wait until an element's label contains text (fails if not)
//   gone:id              wait until it no longer exists (fails if it stays)
//   absent:text          fail if an element's label contains text
//   type:text            type into the focused field, one character at a time
//   clear:n              press delete n times
//   sys:A/B              tap a system button labelled A or B (permission prompt, share sheet,
//                        the message composer's buttons)
//   other:bundle.id      print another app's tree (to find a system screen's buttons)
//   alert:text           tap a button in the app's alert
//   scrollto:id          swipe up until the element is on screen, then wait for the list to rest
//   swipe:up|down|left|right   drag:x1,y1,x2,y2 (a slow drag: swipe-back, sheet dismiss)
//   wait:s   point:x,y (tap a point)   shot:name (screenshot)
//   at:ms                wait until that wall-clock time (ms since 1970): another phone,
//                        driven from the Mac, acts at the same moment (both clocks are NTP's)
//   launch (fresh start, state kept)   open (bring to front)   home (home button)
//   dump (the whole tree)   ids (every testID)   texts (every text)
//   trail:text           wait until the app's trail has a new line (since the last trail
//                        step) containing text
//   diag                 the app's trail since the last read; also printed after every FAIL
//                        and at the end of every journey
//   timeout:s            how long expect/see/gone wait from now on (default 10)
//   ?step                optional: only if it shows up within 3 s (SKIP, not FAIL, if not)
//
// Prints "OK step 123ms", "FAIL step (why)", "SKIP step", and "END journey" when a journey got
// to its last step. Any FAIL fails the test, so the run's exit code tells the truth. Times run
// from the step's start to the screen showing it.
final class Steps: XCTestCase {
  // XCTest waits for the app to be "idle" before every tap. React Native (new architecture)
  // never sends the "animations complete" signal, so every tap waited 60 s while the app sat
  // at 1% CPU. The journeys wait for the exact element they need instead, which is also what
  // makes their timings mean something.
  override class func setUp() {
    super.setUp()
    guard let cls = NSClassFromString("XCUIApplicationProcess") else { return }
    for name in ["waitForQuiescenceIncludingAnimationsIdle:", "waitForQuiescenceIncludingAnimationsIdle:isPreEvent:"] {
      guard let method = class_getInstanceMethod(cls, NSSelectorFromString(name)) else { continue }
      let skip: @convention(block) (AnyObject) -> Void = { _ in }
      method_setImplementation(method, imp_implementationWithBlock(skip))
    }
  }

  func testJourney() {
    // Line by line: scripts that drive another phone react to these lines as they come
    // (stdout to a pipe is otherwise held until the run ends).
    setvbuf(stdout, nil, _IOLBF, 0)
    continueAfterFailure = true
    let env = ProcessInfo.processInfo.environment
    let steps = (env["STEPS"] ?? "").components(separatedBy: "|")
    guard let bundle = env["APP_BUNDLE_ID"], !bundle.isEmpty else {
      XCTFail("APP_BUNDLE_ID is not set (phone.sh passes TEST_RUNNER_APP_BUNDLE_ID)")
      return
    }
    let app = XCUIApplication(bundleIdentifier: bundle)
    let board = XCUIApplication(bundleIdentifier: "com.apple.springboard")
    // Apple's message composer runs in its own process, not in the app.
    let composer = XCUIApplication(bundleIdentifier: "com.apple.MobileSMS.compose")
    if app.state != .runningForeground { app.activate() }
    var timeout: TimeInterval = 10
    var journey = ""
    var broken = false

    func el(_ id: String) -> XCUIElement {
      app.descendants(matching: .any).matching(identifier: id).firstMatch
    }
    func labelled(_ text: String, contains: Bool = true) -> XCUIElement {
      let p = contains ? NSPredicate(format: "label CONTAINS %@", text) : NSPredicate(format: "label == %@", text)
      return app.descendants(matching: .any).matching(p).firstMatch
    }
    /// The element's frame when it is on screen now, from ONE snapshot (nil when it is not).
    /// exists, isHittable and frame are three lookups; an element that leaves in between (a
    /// screen closing itself) is an XCTest error that ends the whole run, not a false.
    func onScreen(_ e: XCUIElement) -> CGRect? {
      guard let snap = try? e.snapshot() else { return nil }
      let f = snap.frame, screen = app.frame
      guard !f.isEmpty, screen.contains(CGPoint(x: f.midX, y: f.midY)) else { return nil }
      return f
    }
    /// The trail's lines, from one snapshot (nil when the app or its trail is not there).
    func trailLines() -> [String]? {
      guard let snap = try? el("diag").snapshot() else { return nil }
      return snap.label.components(separatedBy: "\n")
    }
    /// Polls every 100 ms (waitForExistence checks about once a second).
    func until(_ limit: TimeInterval, _ check: () -> Bool) -> Bool {
      let end = Date().addingTimeInterval(limit)
      repeat {
        if check() { return true }
        Thread.sleep(forTimeInterval: 0.1)
      } while Date() < end
      return check()
    }
    // The app's own trail (diag.ts): one invisible element whose label is the lines.
    var printed = Set<String>()
    var trailSeen = Set<String>()
    func printDiag() {
      guard let lines = trailLines() else { print("DIAG (no trail: not a test build, or the app is not running)"); return }
      for line in lines where !line.isEmpty && line != "-" && !printed.contains(line) {
        printed.insert(line)
        print("DIAG \(line)")
      }
    }
    func shot(_ name: String) {
      let a = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
      a.name = "\(journey.isEmpty ? "adhoc" : journey)--\(name)"
      a.lifetime = .keepAlways
      add(a)
    }

    for raw in steps {
      var s = raw.trimmingCharacters(in: .whitespaces)
      if s.isEmpty { continue }
      if s.hasPrefix("journey:") {
        // The trail to the end, and END when the last step was reached (the summary ignores an
        // END before the first JOURNEY).
        if !broken { printDiag() }
        print("END \(journey.isEmpty ? "steps" : journey)")
        journey = String(s.dropFirst("journey:".count))
        broken = false
        timeout = 10
        print("JOURNEY \(journey)")
        continue
      }
      if broken { print("SKIP \(s) (after a failure)"); continue }
      let optional = s.hasPrefix("?")
      if optional { s.removeFirst() }
      let limit = optional ? 3 : timeout
      let start = Date()
      func ms() -> Int { Int(Date().timeIntervalSince(start) * 1000) }
      func ok() { print("OK \(s) \(ms())ms") }
      func fail(_ why: String = "") {
        if optional { print("SKIP \(s)"); return }
        print("FAIL \(s)\(why.isEmpty ? "" : " (\(why))") after \(ms())ms")
        shot("FAIL")
        printDiag()
        XCTFail("\(journey): \(s)")
        broken = true
      }
      // A target still moving (a sheet rising with the keyboard) gets the tap where it WAS, so
      // tap only once its frame is the same on two polls 100 ms apart, at that frame's centre
      // (e.tap() would look the element up again, and it may have closed in between).
      func tapWhenThere(_ e: XCUIElement) {
        var last = CGRect.null
        if until(limit, {
          guard let now = onScreen(e) else { last = .null; return false }
          defer { last = now }
          return now == last
        }) {
          app.coordinate(withNormalizedOffset: .zero).withOffset(CGVector(dx: last.midX, dy: last.midY)).tap()
          ok()
        } else { fail(e.exists ? "not on screen" : "not found") }
      }

      let k: String, v: String
      if let c = s.firstIndex(of: ":") {
        k = String(s[..<c]); v = String(s[s.index(after: c)...])
      } else { k = s; v = "" }

      switch k {
      case "tap": tapWhenThere(el(v))
      case "label", "has": tapWhenThere(labelled(v, contains: k == "has"))
      case "expect": if until(limit, { el(v).exists }) { ok() } else { fail() }
      case "see": if until(limit, { labelled(v).exists }) { ok() } else { fail() }
      case "gone": if until(limit, { !el(v).exists }) { ok() } else { fail("still there") }
      case "absent": if labelled(v).exists { fail("present") } else { ok() }
      case "either":
        let ids = v.components(separatedBy: "/")
        var found: String?
        if until(limit, { found = ids.first { el($0).exists }; return found != nil }) {
          print("OK \(s) -> \(found!) \(ms())ms")
        } else { fail() }
      case "type":
        for ch in v {
          app.typeText(String(ch))
          Thread.sleep(forTimeInterval: 0.12) // controlled React Native fields drop faster typing
        }
        ok()
      case "clear":
        app.typeText(String(repeating: XCUIKeyboardKey.delete.rawValue, count: Int(v) ?? 1)); ok()
      case "sys":
        let names = v.components(separatedBy: "/")
        var target: XCUIElement?
        if until(limit, {
          // firstMatch: some system prompts carry two buttons with the same label, and a
          // subscript that matches two throws and ends the whole run.
          target = names.lazy.flatMap { n in
            [board, app, composer].map {
              $0.buttons.matching(NSPredicate(format: "label == %@ OR identifier == %@", n, n)).firstMatch
            }
          }.first { $0.exists }
          return target != nil
        }) { target!.tap(); ok() } else { fail() }
      case "alert": tapWhenThere(app.alerts.buttons[v])
      case "scrollto":
        let e = el(v)
        var n = 0
        while onScreen(e) == nil && n < 12 { app.swipeUp(velocity: .slow); n += 1 }
        // Wait for the list to come to rest: on iOS a touch on a moving list only stops it, so
        // a tap right after a swipe never reaches the button.
        var last = CGRect.null
        _ = until(3) {
          let now = onScreen(e) ?? .null
          defer { last = now }
          return now == last
        }
        if onScreen(e) != nil { ok() } else { fail() }
      case "swipe":
        switch v {
        case "up": app.swipeUp()
        case "down": app.swipeDown()
        case "left": app.swipeLeft()
        default: app.swipeRight()
        }
        ok()
      case "drag":
        let p = v.split(separator: ",").compactMap { Double($0) }
        guard p.count == 4 else { fail("drag:x1,y1,x2,y2"); continue }
        let o = app.coordinate(withNormalizedOffset: .zero)
        o.withOffset(CGVector(dx: p[0], dy: p[1]))
          .press(forDuration: 0.15, thenDragTo: o.withOffset(CGVector(dx: p[2], dy: p[3])))
        ok()
      case "wait": Thread.sleep(forTimeInterval: Double(v) ?? 1); ok()
      case "at":
        let left = (Double(v) ?? 0) / 1000 - Date().timeIntervalSince1970
        if left > 0 { Thread.sleep(forTimeInterval: left) }
        ok()
      case "point":
        let p = v.split(separator: ",").compactMap { Double($0) }
        guard p.count == 2 else { fail("point:x,y"); continue }
        app.coordinate(withNormalizedOffset: .zero).withOffset(CGVector(dx: p[0], dy: p[1])).tap(); ok()
      case "shot": shot(v); ok()
      case "launch": app.terminate(); printed.removeAll(); trailSeen.removeAll(); app.activate(); ok()
      case "open": app.activate(); ok()
      case "home": XCUIDevice.shared.press(.home); ok()
      case "timeout": timeout = Double(v) ?? 10; ok()
      case "diag": printDiag()
      case "trail":
        // Only lines that arrived since the previous trail step (or launch) count, so a
        // sequence (speaker on, then off) cannot be satisfied by an older line. Only the lines
        // up to the match count as seen; later ones are left for the next trail step.
        var seen: ArraySlice<String> = []
        if until(limit, {
          guard let lines = trailLines() else { return false }
          guard let i = lines.firstIndex(where: { !trailSeen.contains($0) && $0.contains(v) }) else { return false }
          seen = lines[...i]
          return true
        }) {
          trailSeen.formUnion(seen)
          ok()
        } else { fail("not in the app's trail") }
      case "other": print("<<<DUMP\n\(XCUIApplication(bundleIdentifier: v).debugDescription)\nDUMP>>>")
      case "dump": print("<<<DUMP\n\(app.debugDescription)\nDUMP>>>")
      case "ids":
        for l in app.debugDescription.components(separatedBy: "\n") where l.contains("identifier:") {
          print("ID " + l.trimmingCharacters(in: .whitespaces).prefix(200))
        }
      case "texts":
        for l in app.debugDescription.components(separatedBy: "\n") where l.contains("label: ") {
          if let r = l.range(of: "label: ") { print("TEXT " + l[r.upperBound...].prefix(160)) }
        }
      default: fail("unknown step")
      }
    }
    // The trail to the end, and END when the last step was reached (steps without a journey too).
    if !broken { printDiag() }
    print("END \(journey.isEmpty ? "steps" : journey)")
  }
}
