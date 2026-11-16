import SwiftUI

// An empty host: XCUITest needs one, but the runner drives the app under test by bundle id.
@main struct Host: App { var body: some Scene { WindowGroup { Text("Phone runner") } } }
