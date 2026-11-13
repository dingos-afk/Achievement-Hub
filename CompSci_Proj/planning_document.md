# Achievement Hub — Planning Document

## Purpose
Achievement Hub is a website for organizing video games and tracking
the achievements a user has earned in those games.

## Intended users
People who want a central place to view their game collection and
manually track achievements.

## Main features
- Search for games using Steam Store search.
- Add selected games to a personal library.
- Retrieve public achievement definitions from Steam.
- Manually mark achievements as completed.
- View completion percentages.
- Edit a profile and game display settings.

## Routes
1. `Home` — homepage and progress summary.
2. `Profile` — profile editing.
3. `Settings` — game sorting preference.
4. `library` — Steam game search and adding games.
5. `individual_game` — one game's achievements and progress.
6. `view_Games` — the user's game collection.
7. `view_Achievements` — achievement list and completion editor.

## Data models
- `Game`: name, Steam App ID, image, and priority.
- `Achievement`: name, game name, category, description,
  completion status, Steam identifier, and icon.
- `State`: username, games, achievements, completed-game count,
  profile description, consoles, sort preference, search results,
  search priority, and status message.

## External service
The FastAPI backend calls Steam's Store search endpoint and
GetSchemaForGame endpoint. No Steam user login or player account
achievement access is used.

## Limitations to address before final release
- Drafter State is temporary and resets when the browser reloads.
- Add persistent storage before presenting this as a permanent
  multi-user achievement tracker.
- Steam does not provide a rarity value in the schema response used
  here, so the initial category is shown as "Unspecified".
- Configure production CORS with the deployed website's exact origin.
- Replace the local backend URL with the deployed FastAPI URL.
