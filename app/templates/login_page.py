from __future__ import annotations

from .components import esc
from .layout import render_layout


def render_login_page(error: str | None = None) -> str:
    error_html = f'<p class="form-error">{esc(error)}</p>' if error else ""
    body = f"""
    <section class="login-card">
      <div class="hero-copy">
        <p class="eyebrow">Internal portal</p>
        <h2>Track incidents, follow-ups and release work in one place.</h2>
        <p>
          Seeded accounts are included so the environment is useful immediately.
          Use <code>yuki</code> / <code>travel123</code> to sign in.
        </p>
      </div>
      <form class="login-form" method="post" action="/login">
        <label>Username<input name="username" autocomplete="username" required /></label>
        <label>Password<input name="password" type="password" autocomplete="current-password" required /></label>
        {error_html}
        <button type="submit">Open Travel Editor</button>
      </form>
    </section>
    """
    return render_layout(title="Travel Editor Login", body=body, page_id="login")
