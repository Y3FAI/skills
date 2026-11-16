# Google Play Console: statistics and store listing

Use the driver in your own logged-in browser (see SKILL.md). Play Console is an Angular app: wait about 8 s after load.

## Find the app

1. `open https://play.google.com/console/` → it may ask "Choose developer account": click the account name.
2. Home lists every app with **Monthly active devices** (28 days). Get app links:
   `eval` → `[...document.querySelectorAll("a")].map(a=>a.href).filter(h=>h.includes("/app/"))`
   They look like `/developers/<devId>/app/<appId>/app-dashboard`.

## Statistics page is set by its URL

```
/developers/<devId>/app/<appId>/statistics
  ?metrics=ENGAGEMENT_MONTHLY_ACTIVE_USERS-ACQUISITION_UNSPECIFIED-UNIQUE-PER_INTERVAL-DAY
  &dimension=COUNTRY
  &dimensionValues=OVERALL%2CEG%2CSA%2CDZ
  &dateRange=2025_11_1-2026_11_9
  &tab=APP_STATISTICS
```

- **Metric keys** seen so far: `ENGAGEMENT_MONTHLY_ACTIVE_USERS-ACQUISITION_UNSPECIFIED-UNIQUE-PER_INTERVAL-DAY` (MAU), `ACTIVE_USERS-ALL-UNIQUE-PER_INTERVAL-DAY` (installed audience, the default). For any other metric, pick it in the UI and read `location.href`.
- An invalid metric key (for example `...-PER_INTERVAL-MONTH`) falls back quietly to installed audience. Check the metric name on the page.
- **dateRange**: `YYYY_M_D-YYYY_M_D`. A 12-month MAU chart (daily points) shows the trend.
- **dimensionValues**: `OVERALL` plus at most about **9 countries**. With 10 it shows "An unexpected error has occurred".
- MAU data lags about a week behind today.

## Picking the metric in the UI

The metric chip is `button[aria-haspopup=listbox]` with text "Installed audience". Matching on text alone hits the chart legend instead. Groups: Users, Devices, Reach, Acquisition, Activation, **Engagement** (DAU, MAU, monthly active devices, DAU/MAU, usage time, returning users), Retention, Ratings, Quality. Options are `material-select-item`.

## Top countries

Click the "All countries / regions" chip. The picker lists countries **sorted by size**. Read the list and close it.

## Screenshots

- Chart: `scroll` to "Configure report", then `shot`. Data table: `scroll` to "Data table", then `shot`. The table shows the latest day first, with the % of total.
- With OVERALL + 8 countries the table fits the width. A 9th column goes behind a horizontal scroll bar.
- Move the mouse to an empty spot first (`mouse x=1200 y=60`), or a chart tooltip covers the table. The left edge opens the side menu.
- The home page lists all of the user's apps. Don't send it to third parties.

## Store listing: change the icon or other graphics

Editor: `/developers/<devId>/app/<appId>/store-listings/default/edit`. It has two steps, **Assets** and **Review**, with a "Select a language to edit" picker and a pinned **Next language** button.

- **Translations show the default language's graphics as if they were their own** ("1/1" with a delete button, same image URL). Usually they are inherited. Change the default first, then use **Next language** to check each translation: one that still shows the old image has its own copy and needs the same change.
- **Read the field from the DOM:** find the leaf element whose text is `App icon`, walk up to the parent that holds an `img`, and read `img.src`. Each image has a stable `lh3.googleusercontent.com/<id>` URL, so you can tell old from new without a screenshot. Search only inside the field, because the sidebar shows the app icon too.
- **Add assets** opens an asset-library side panel (Upload, Add from Drive, and earlier uploads). There is no `input[type=file]` on the page until you choose Upload. To reuse a library image: run `mouse` over its row, find `a[aria-label="Select button"]` inside the row, `clickxy` on it, then `rclick` the **Add** button (`add_photo_alternate Add`).
- The field allows **1/1**. Adding a second image shows "2/1 Too many images". Delete the old one with the `delete` button next to its `img`, then check that the field shows only the new image, at 1/1.
- **Save as draft** saves every language at once. It worked when both Discard and Save as draft are greyed out and the footer says "Your changes have been saved". The listing then shows "Live · Draft changes".

## Sending it for review

1. In the editor, click **Next** to open the Review step. The **AI asset declaration** radio ("Don't label assets" or "Label assets as created or edited using AI") has no default, and it is the user's call, so ask. The Review step shows the assets that will be sent, so check the icon URL there too.
2. **Save** → a dialog says "Your change has been saved" → **Go to overview**.
3. Publishing overview lists "Changes not yet submitted for review" with one row per item (for example "Default store listing · Change app icon"). **Submit N changes for review** → confirm with **Send changes for review**. This sends the change to Google, so get the user's go-ahead first.
4. Quick checks run for up to about 14 minutes, then the change goes to review. If managed publishing is off, it goes live once approved. **Remove changes** withdraws it while it is still in review.
