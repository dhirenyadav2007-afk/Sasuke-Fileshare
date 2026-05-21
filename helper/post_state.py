# helper/post_state.py
# ─────────────────────────────────────────────────────────────────────────────
# Shared state for admin multi-step command sessions.
# Imported by channel_post.py, post.py and fbatch.py — keeping them
# all decoupled from each other.
# ─────────────────────────────────────────────────────────────────────────────

# Full session data for /post and /edit flows
# { user_id: { 'mode', 'step', 'channel_id', 'content_msg', 'buttons', ... } }
sessions: dict[int, dict] = {}

# General "busy" registry — ANY admin command that requires the user to send
# plain messages adds the user_id here for the duration of the flow.
# channel_post.py checks this before forwarding to the DB channel.
# Usage:  active.add(uid)  /  active.discard(uid)
active: set[int] = {}
