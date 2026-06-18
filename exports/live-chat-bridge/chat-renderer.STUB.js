/* =============================================================================
 * live-chat-bridge / chat-renderer.STUB.js
 * -----------------------------------------------------------------------------
 * STATUS: UNINTEGRATED STUB — NOT WIRED INTO ANY LIVE PORTAL UI.
 * Created 2026-06-18 for the DO<->Portal live-chat bridge (portal side).
 *
 * BLOCKER: The live portal chat UI location is UNRESOLVED. This server
 * (tools/purebrain_log_server.py) is API-only and serves NO static assets or
 * templates, so the renderer cannot be auto-wired. Candidate locations for the
 * real chat UI (must be confirmed before integration):
 *   - exports/*.html  +  exports/*.js   (scattered; not confidently identified)
 *   - /home/jared/purebrain_portal/     (OUT-OF-REPO; own .bak conventions;
 *                                         NOT part of this git repository)
 * NOTE: exports/777-command-center/api/chat.js is a DIFFERENT system and is
 *       confirmed NOT the portal live-chat UI.
 *
 * TODO(contract): locate live portal chat UI + wire this renderer —
 *                 confirm with Morphe/Jared.
 * ============================================================================= */

/**
 * Render an inbound bridge message into the portal chat UI.
 *
 * PLACEHOLDER ONLY — this skeleton does not touch the DOM because the target
 * container/markup is unknown. Wire the body once the chat UI is located.
 *
 * @param {Object} msg
 * @param {string} msg.conversation_id - conversation/thread identifier
 * @param {string} msg.sender          - message sender (e.g. 'agent' | 'user')
 * @param {string} msg.text            - message body
 * @param {string} msg.ts             - ISO-8601 timestamp
 * @returns {void}
 */
function renderInboundBridgeMessage(msg) {
  // TODO(contract): confirm payload schema with Morphe before relying on fields.
  if (!msg || typeof msg !== 'object') {
    console.warn('[live-chat-bridge] renderInboundBridgeMessage: invalid msg', msg);
    return;
  }

  const { conversation_id, sender, text, ts } = msg;

  // STUB: no DOM target known yet. Log so integration can be observed in dev.
  console.debug('[live-chat-bridge][STUB] inbound message', {
    conversation_id,
    sender,
    text,
    ts,
  });

  // TODO(contract): once the chat UI container is located, append a message
  // bubble for `conversation_id`, attributed to `sender`, with `text` and `ts`.
}

// Export for both module and global usage without assuming a bundler.
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { renderInboundBridgeMessage };
}
