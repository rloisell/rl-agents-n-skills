# EF Core Knowledge

Recorded discoveries from .NET + Pomelo MariaDB engagements:

- **2026-02-27 (`[engagement]`):** Pomelo TCP connection on macOS Homebrew MariaDB — socket path auth is not needed with a password-authenticated user. Connection uses `Server=localhost;Port=3306;`.
- **2026-02-27 (`[engagement]`):** `db.Database.Migrate()` in `Program.cs` — `InitialCreate` migration applied cleanly on `<project>_dev` DB on first run.
- **2026-02-27 (`[engagement]`):** Quartz.NET background job scheduler requires its own `AddQuartz()` DI extension. Keep Quartz config separate from EF Core registration to avoid `Program.cs` bloat.
