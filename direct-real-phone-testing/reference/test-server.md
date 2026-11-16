# A local test server and fake data

When the app has a backend, the phone talks to a copy of it running on the Mac, filled with fake data that's the same on every run. Then journeys can check exact content (`see:Sample Item 1`), nothing touches production, and no real person's data is ever on screen or in a screenshot.

## The server

- Bind to all interfaces so the phone reaches it over Wi-Fi: Cloudflare `wrangler dev --local --ip 0.0.0.0 --port 8811 --persist-to e2e/phone/.out/state`, `next dev -H 0.0.0.0`, `uvicorn --host 0.0.0.0`, and so on.
- Keep the server's state under `e2e/phone/.out/` (gitignored), separate from your normal dev state.
- **Refuse to start when the port is taken.** A stale server answering on the same port silently serves old code.
- Secrets: read them from a gitignored env file. When one is missing, fall back to test values and say so. Never print a value. Print key names only.
- Give it a health endpoint (`HEALTH_PATH` in `phone.env`). `phone.sh test` checks it and warns when the server is down.
- The phone and the Mac must be on the same Wi-Fi. A guest network or client isolation blocks it. `phone.sh build` bakes in `en0`'s address. Set `PHONE_LAN_IP` when the Mac uses another interface. If the Mac's address changes, rebuild.

## Fake data

- Generate it with a script (`e2e/phone/fixtures/make.py` or `.mjs`). Never take it from a production export.
- Make it shaped like real life: some rows without photos, long names, empty states, a history spread over days, right-to-left text if the app is used that way.
- `seed.sh <state dir>`: run the migrations, then load the fake data, so every run starts from the same state. `phone.sh test` calls it with `QUICK=1` (skip work that hasn't changed, such as re-uploading unchanged photos).
- **Real-looking contact data is still fake.** When the fake phone numbers or emails look real, never press send in a composer they open. Journeys cancel composers and check the cancel through the trail.
- **The user's own data stays on the phone.** If the app can import contacts, photos or files, journeys refuse that prompt (`sys:Don't Allow`) unless the user asks for it. Don't upload a real address book to a test server.
- The test account: sign in once by hand, or seed a session the app restores at launch. A journey that signs out would sign the user out of their real build.

## Package scripts (example)

```json
"phone:server": "bash e2e/phone/scripts/server.sh",
"phone:seed": "bash e2e/phone/scripts/seed.sh e2e/phone/.out/state",
"phone:build": "bash e2e/phone/scripts/phone.sh build",
"phone:runner": "bash e2e/phone/scripts/phone.sh runner",
"phone:test": "bash e2e/phone/scripts/phone.sh test",
"phone:android": "bash e2e/phone/scripts/android.sh"
```

`server.sh` and `seed.sh` are project-specific: write them for the project's backend.
