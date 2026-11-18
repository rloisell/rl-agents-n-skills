# .NET JWT Validation & Backchannel Logout

## Package

```bash
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
```

## Program.cs Configuration

```csharp
// OIDC JWT bearer authentication — validates tokens from Keycloak
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Oidc:Authority"];
        // e.g. https://loginproxy.gov.bc.ca/auth/realms/standard
        options.Audience  = builder.Configuration["Oidc:ClientId"];
        options.RequireHttpsMetadata = !builder.Environment.IsDevelopment();
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer           = true,
            ValidateAudience         = true,
            ValidateLifetime         = true,
            ClockSkew                = TimeSpan.FromSeconds(60),
        };
    });

builder.Services.AddAuthorization();
// ...
app.UseAuthentication();
app.UseAuthorization();
```

## Extracting Claims

```csharp
// returns the sub claim (Keycloak user ID)
private static Guid? GetUserId(ClaimsPrincipal user)
    => Guid.TryParse(user.FindFirstValue(ClaimTypes.NameIdentifier), out var id)
        ? id : null;
```

## Backchannel Logout (.NET API)

```csharp
// POST /logout/backchannel — handles Keycloak backchannel logout token
[HttpPost("/logout/backchannel")]
[AllowAnonymous]
[Consumes("application/x-www-form-urlencoded")]
public async Task<IActionResult> BackchannelLogout([FromForm] string logout_token)
{
    // 1. Validate logout_token JWT: issuer, audience, iat, jti
    // 2. Extract 'sub' or 'sid' claim
    var sub = User.FindFirstValue(ClaimTypes.NameIdentifier) ?? "(unknown)";
    // 3. Invalidate any server-side session or cached token for that sub/sid
    // 4. Return 200 OK or 400 Bad Request
    _logger.LogInformation("Backchannel logout received for sub={Sub}", sub);
    return Ok();
}
```
