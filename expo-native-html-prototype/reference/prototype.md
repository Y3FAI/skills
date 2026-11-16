# Building the HTML prototype

## Directions

- One file, e.g. `playground/directions.html`: 3–5 phones side by side at device size (390×844 for iPhone, 412×915 for Android), each a different idea, not five versions of one idea. Label each with a one-line thesis ("tiles: faces first", "list: dense and fast").
- Use the same real-looking data in all of them, so the user compares design, not content. Include the awkward cases: a long name, no photo, ten items, an empty screen.
- A few page toggles (tone: warm/neutral/cool, light/dark) are fine. The aim is a quick pick.
- After the pick, save the file under `playground/archive/`. Directions get revisited.
- Keep it fast. If producing directions takes long, simplify. The user wants to react, not wait.

## The prototype

Start from `templates/prototype.html` and keep its machinery. Replace the content.

**Structure**
- `.phone` is the device: a fixed size, rounded, `overflow:hidden`. Everything app-like lives inside it. The side panel is the page around it.
- Screens are absolutely positioned `.layer`s. Home sits underneath and pushed screens go on top (`push(id)` / `pop()`). Modals and sheets live above the layers.
- The keyboard is a grey block of the real height (about 300 pt/dp). Fields focus it, and sheets ride on top of it. Designing without it is how layouts break on the phone.
- The status bar and home indicator are decoration, but keep content clear of them (top inset 54 pt on iPhone, 40 dp on Android; bottom 34 pt / 24 dp).

**Motion**
- Every duration and curve sits in the `IOS` and `ANDROID` objects. The app copies these numbers. iOS uses UIKit's sheet/navigation curve `cubic-bezier(0.32,0.72,0,1)`. Android uses Material 3's emphasized decelerate / accelerate and standard curves.
- `T(ms)` applies slow motion (×5) so the user can study a transition. `reduced()` swaps movement for short crossfades, which is how Reduce Motion behaves on the phone.
- Animate `transform` and `opacity`. For a picture growing into a screen, fly a copy of the picture between the two frames and fade the rest of the screen around it. Don't reveal the target screen through a clip: the source has to visibly become the destination.
- Gestures follow the finger 1:1 and settle with velocity: release past about a third, or a quick flick, completes the gesture; otherwise it springs back.

**Platform modes**
- iPhone: push from the trailing side with parallax, a full-screen swipe back, a form sheet with a grabber, a frosted round +, a centred title with a chevron, and a dim while the finger is down.
- Android: a shared-axis push, predictive back (the screen shrinks and shows what's underneath as you drag from an edge), a Material bottom sheet with a drag handle, a FAB at the bottom end, a 64 dp top bar with the title at the start, and a ripple.
- RTL: `dir="rtl"` on the phone. Pushes come from the left and back gestures mirror. Use logical CSS properties (`inset-inline-start`, `margin-inline-end`) everywhere so nothing needs a second layout.

**The panel**
- Platform, language/direction, theme, and Motion (slow, Reduce Motion) always.
- "Pick one" groups only for open decisions, each option with a bold name and one line of what it does. After the user picks, mark it ("Picked") or delete the group.
- "Try": short instructions for what to do, especially hidden gestures. "Notes": what's simplified, for example "the system prompt is drawn by iOS in the real app".
- Save the panel state in `localStorage`, wrapped in try/catch, so a reload keeps the user's place.

**Content**
- Use an `S` strings object per language and a data array. Nothing user-visible is hard-coded in the markup, so translating or swapping content is one edit.
- Make sample data shaped like real data: varied lengths, missing images, many items.

## Checking the prototype itself

`node tools/shoot.mjs prototype.html shots set:platform=android 'click:.tile[data-i="1"]' wait:150 shot:mid wait:600 shot:open` saves screenshots and fails on any page error. Use it after every change to the machinery, and to capture states for the side-by-side check against the phone. Turn on slow motion (`click:#slow`) to catch mid-transition frames.
