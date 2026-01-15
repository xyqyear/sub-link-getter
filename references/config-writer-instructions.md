# Site Configuration Writer Instructions

This document describes how to create a site configuration JSON object for the subscription link getter application.

## Required Information from User

Before writing a configuration, you need the following from the user:

1. **product_url** - The URL to the product/subscription page (redirects to login if not authenticated)
2. **Login page HTML** - Either the full login page or just the login form section
3. **Product page HTML** - Either the full product page or just the subscription link container section
4. **Credentials** - Username and password for the site

## Configuration Fields

### Basic Information

| Field         | Type   | Required | Description                                           |
| ------------- | ------ | -------- | ----------------------------------------------------- |
| `id`          | string | Yes      | Unique identifier for the site (lowercase, no spaces) |
| `name`        | string | Yes      | Human-readable display name                           |
| `product_url` | string | Yes      | URL to access (provided by user)                      |

### Login Selectors

Analyze the login form HTML to identify these selectors:

| Field                      | Type   | Required | Description                                             |
| -------------------------- | ------ | -------- | ------------------------------------------------------- |
| `login_wait_selector`      | string | Yes      | Selector that identifies the login page/form is present |
| `post_login_wait_selector` | string | Yes      | Selector that appears after successful login            |
| `username_selector`        | string | Yes      | Selector for the username/email input field             |
| `password_selector`        | string | Yes      | Selector for the password input field                   |
| `login_button_selector`    | string | Yes      | Selector for the login/submit button                    |
| `captcha_image_selector`   | string | No       | Selector for captcha image (if present)                 |
| `captcha_input_selector`   | string | No       | Selector for captcha input field (if present)           |
| `captcha_retry_count`      | int    | No       | Number of captcha recognition attempts (default: 2)     |

### Credentials

| Field      | Type   | Required | Description          |
| ---------- | ------ | -------- | -------------------- |
| `username` | string | Yes      | Login username/email |
| `password` | string | Yes      | Login password       |

### Subscription Extraction Selectors

Analyze the product page HTML to identify these selectors:

| Field                             | Type   | Required | Description                                                    |
| --------------------------------- | ------ | -------- | -------------------------------------------------------------- |
| `subscription_label_selector`     | string | Yes      | Selector for subscription type labels (e.g., "Clash", "V2Ray") |
| `subscription_group_selector`     | string | Yes      | Selector for subscription groups (paired with labels by index) |
| `subscription_url_type`           | string | Yes      | Either `"input"` or `"copy"`                                   |
| `subscription_url_selector`       | string | Yes      | Selector within group for the URL element                      |
| `subscription_url_attribute`      | string | No       | For `"copy"` type: the data attribute containing the URL       |
| `subscription_name_pattern`       | string | No       | Regex to filter subscription type (default: `".*"`)            |
| `subscription_url_retry_count`    | int    | No       | Retries for URL extraction (default: 10)                       |
| `subscription_url_retry_delay_ms` | int    | No       | Delay between retries in ms (default: 250)                     |

### Content Validation

| Field                | Type   | Required | Description                                                        |
| -------------------- | ------ | -------- | ------------------------------------------------------------------ |
| `content_validation` | string | No       | String that must exist in fetched content (default: `"allow-lan"`) |

## How to Identify Selectors

### Login Form Analysis

1. **login_wait_selector**: Find a unique container or class that wraps the login form

   - Look for `<form>` elements with login-related classes
   - Look for container divs with classes like `login`, `signin`, `auth`

2. **username_selector**: Find the email/username input

   - Look for `<input>` with `type="email"` or `type="text"`
   - Check `name` attribute (often `username`, `email`, `user`)
   - Check `id` attribute for unique identifiers

3. **password_selector**: Find the password input

   - Look for `<input>` with `type="password"`
   - Check `name` or `id` attributes

4. **login_button_selector**: Find the submit button

   - Look for `<button type="submit">` or `<input type="submit">`
   - Check for classes or IDs related to login

5. **captcha selectors** (if present):
   - Image: Look for `<img>` elements with captcha-related classes/IDs
   - Input: Look for additional `<input>` fields for captcha text

### Product Page Analysis

1. **subscription_label_selector**: Find elements containing subscription type names

   - Look for labels, spans, or divs showing "Clash", "V2Ray", "Shadowsocks", etc.

2. **subscription_group_selector**: Find the container that groups each subscription type

   - This should be a repeating element that contains both the label and URL
   - Labels and groups are paired by index (first label matches first group)

3. **subscription_url_type**: Determine how the URL is stored

   - `"input"`: URL is in an `<input>` field's value
   - `"copy"`: URL is in a data attribute (like `data-clipboard-text` or `data-copy`)

4. **subscription_url_selector**: Find the element containing the URL within each group

   - For `"input"` type: the input element itself
   - For `"copy"` type: the button/link with the copy functionality

5. **subscription_url_attribute**: For `"copy"` type only
   - Common attributes: `data-clipboard-text`, `data-copy`, `data-url`

## Questions to Ask if Information is Missing

If the user hasn't provided sufficient information, ask:

1. "What is the product URL for this site?"
2. "Can you provide the HTML of the login form?"
3. "Can you provide the HTML of the subscription links section on the product page?"
4. "What are your login credentials (username and password) for this site?"
5. "Does this site have a captcha on the login page?"
6. "Which subscription type do you want to extract? (e.g., Clash, V2Ray)"
7. "What string should be present in the subscription content to validate it? (default: allow-lan)"

## Example Configuration

### Example 1: Site without Captcha (copy type)

**Login Form HTML:**

```html
<div class="auth-form">
  <h2>Sign In</h2>
  <div class="form-group">
    <label>Email</label>
    <input
      type="email"
      id="user-email"
      name="email"
      placeholder="Enter email"
    />
  </div>
  <div class="form-group">
    <label>Password</label>
    <input
      type="password"
      id="user-pass"
      name="password"
      placeholder="Enter password"
    />
  </div>
  <button type="submit" class="btn-login">Login</button>
</div>
```

**Product Page HTML (subscription section):**

```html
<div class="subscription-container">
  <div class="sub-row">
    <span class="sub-type-name">Clash</span>
    <div class="sub-actions">
      <input type="text" readonly value="" />
      <button class="copy-btn" data-url="https://example.com/sub/abc123/clash">
        Copy
      </button>
    </div>
  </div>
  <div class="sub-row">
    <span class="sub-type-name">V2Ray</span>
    <div class="sub-actions">
      <input type="text" readonly value="" />
      <button class="copy-btn" data-url="https://example.com/sub/abc123/v2ray">
        Copy
      </button>
    </div>
  </div>
  <div class="sub-row">
    <span class="sub-type-name">Shadowsocks</span>
    <div class="sub-actions">
      <input type="text" readonly value="" />
      <button class="copy-btn" data-url="https://example.com/sub/abc123/ss">
        Copy
      </button>
    </div>
  </div>
</div>
```

**Resulting Configuration:**

```json
{
  "id": "example-vpn",
  "name": "Example VPN",
  "product_url": "https://example-vpn.com/dashboard/product/12345",
  "login_wait_selector": ".auth-form",
  "post_login_wait_selector": ".sub-row",
  "username_selector": "#user-email",
  "password_selector": "#user-pass",
  "login_button_selector": ".btn-login",
  "captcha_image_selector": null,
  "captcha_input_selector": null,
  "username": "user@example.com",
  "password": "userpassword123",
  "subscription_label_selector": ".sub-row .sub-type-name",
  "subscription_group_selector": ".sub-row",
  "subscription_url_type": "copy",
  "subscription_url_selector": "button.copy-btn[data-url]",
  "subscription_url_attribute": "data-url",
  "subscription_name_pattern": "Clash",
  "content_validation": "allow-lan"
}
```

**Selector Mapping Explanation:**

| Config Field                  | HTML Element                               | Selector                    |
| ----------------------------- | ------------------------------------------ | --------------------------- |
| `login_wait_selector`         | `<div class="auth-form">`                  | `.auth-form`                |
| `post_login_wait_selector`    | `<div class="sub-row">`                    | `.sub-row`                  |
| `username_selector`           | `<input id="user-email">`                  | `#user-email`               |
| `password_selector`           | `<input id="user-pass">`                   | `#user-pass`                |
| `login_button_selector`       | `<button class="btn-login">`               | `.btn-login`                |
| `subscription_label_selector` | `<span class="sub-type-name">`             | `.sub-row .sub-type-name`   |
| `subscription_group_selector` | `<div class="sub-row">`                    | `.sub-row`                  |
| `subscription_url_selector`   | `<button class="copy-btn" data-url="...">` | `button.copy-btn[data-url]` |
| `subscription_url_attribute`  | `data-url` attribute                       | `data-url`                  |

---

### Example 2: Site with Captcha (input type)

**Login Form HTML:**

```html
<form class="signin-form" method="post">
  <div class="input-group">
    <input type="text" name="username" id="loginEmail" placeholder="Email" />
  </div>
  <div class="input-group">
    <input
      type="password"
      name="password"
      id="loginPassword"
      placeholder="Password"
    />
  </div>
  <div class="captcha-group">
    <img src="/captcha.php" id="captchaImg" alt="Captcha" />
    <input
      type="text"
      name="captcha"
      id="captchaInput"
      placeholder="Enter captcha"
    />
  </div>
  <button type="submit" id="submitBtn">Sign In</button>
</form>
```

**Product Page HTML (subscription section):**

```html
<div class="subscribe-panel">
  <div class="subscribe-item">
    <label class="subscribe-label">Clash Subscription</label>
    <div class="subscribe-input-group">
      <input
        type="text"
        class="subscribe-url"
        readonly
        value="https://example.com/api/clash/xyz789"
      />
      <button class="btn-copy">Copy</button>
    </div>
  </div>
  <div class="subscribe-item">
    <label class="subscribe-label">Quantumult X</label>
    <div class="subscribe-input-group">
      <input
        type="text"
        class="subscribe-url"
        readonly
        value="https://example.com/api/quanx/xyz789"
      />
      <button class="btn-copy">Copy</button>
    </div>
  </div>
</div>
```

**Resulting Configuration:**

```json
{
  "id": "another-vpn",
  "name": "Another VPN",
  "product_url": "https://another-vpn.com/client/services/98765",
  "login_wait_selector": ".signin-form",
  "post_login_wait_selector": ".subscribe-panel",
  "username_selector": "#loginEmail",
  "password_selector": "#loginPassword",
  "login_button_selector": "#submitBtn",
  "captcha_image_selector": "#captchaImg",
  "captcha_input_selector": "#captchaInput",
  "captcha_retry_count": 3,
  "username": "myemail@example.com",
  "password": "mypassword456",
  "subscription_label_selector": ".subscribe-item .subscribe-label",
  "subscription_group_selector": ".subscribe-item",
  "subscription_url_type": "input",
  "subscription_url_selector": "input.subscribe-url",
  "subscription_url_attribute": null,
  "subscription_name_pattern": "Clash",
  "content_validation": "allow-lan"
}
```

**Selector Mapping Explanation:**

| Config Field                  | HTML Element                      | Selector                           |
| ----------------------------- | --------------------------------- | ---------------------------------- |
| `login_wait_selector`         | `<form class="signin-form">`      | `.signin-form`                     |
| `post_login_wait_selector`    | `<div class="subscribe-panel">`   | `.subscribe-panel`                 |
| `username_selector`           | `<input id="loginEmail">`         | `#loginEmail`                      |
| `password_selector`           | `<input id="loginPassword">`      | `#loginPassword`                   |
| `login_button_selector`       | `<button id="submitBtn">`         | `#submitBtn`                       |
| `captcha_image_selector`      | `<img id="captchaImg">`           | `#captchaImg`                      |
| `captcha_input_selector`      | `<input id="captchaInput">`       | `#captchaInput`                    |
| `subscription_label_selector` | `<label class="subscribe-label">` | `.subscribe-item .subscribe-label` |
| `subscription_group_selector` | `<div class="subscribe-item">`    | `.subscribe-item`                  |
| `subscription_url_selector`   | `<input class="subscribe-url">`   | `input.subscribe-url`              |

**Key Differences:**

- `subscription_url_type` is `"input"` because the URL is in the input's `value` attribute
- `subscription_url_attribute` is `null` because we read from input value, not a data attribute
- Captcha selectors are populated since this site has captcha

## Selector Best Practices

1. **Prefer IDs over classes** when available (`#inputEmail` vs `.email-input`)
2. **Use specific selectors** to avoid matching unintended elements
3. **Scope selectors** when needed (e.g., `.login-form input[name="email"]`)
4. **Test uniqueness** - ensure selectors match exactly one element (except for subscription groups/labels which are lists)
5. **Use attribute selectors** for inputs without IDs (e.g., `input[name="username"]`)

## Index-Based Pairing

The subscription extraction uses index-based pairing:

- `subscription_label_selector` returns a list of label elements
- `subscription_group_selector` returns a list of group elements
- Label at index 0 corresponds to group at index 0, and so on

Ensure both selectors return elements in the same order.
