/**
 * AI Birth Certificate Generator - certificate-generator.js
 * Renders a beautiful parchment-style birth certificate on HTML5 Canvas.
 * Output: 1200x628px PNG (optimized for social media sharing).
 */

'use strict';

const CERT = {
  WIDTH: 1200,
  HEIGHT: 628,
  COLORS: {
    parchment: '#f5f0e1',
    parchmentDark: '#ede4c8',
    orange: '#f1420b',
    orangeLight: '#fde8e2',
    darkBrown: '#3d2314',
    midBrown: '#7a4f2f',
    lightBrown: '#b08060',
    aiBlue: '#2a93c1',
    aiBlueLight: '#d8eef7',
    white: '#ffffff',
    gold: '#c9982a',
    goldLight: '#f0d890',
  },
  FONTS: {
    serif: 'Georgia, "Times New Roman", serif',
    sans: 'Arial, Helvetica, sans-serif',
  },
};

/**
 * Main entry point - renders the certificate to the given canvas.
 * @param {HTMLCanvasElement} canvas
 * @param {Object} data - { aiName, userName, tagline }
 */
function renderCertificate(canvas, data) {
  canvas.width = CERT.WIDTH;
  canvas.height = CERT.HEIGHT;

  const ctx = canvas.getContext('2d');
  const { aiName, userName, tagline } = data;
  const now = new Date();

  _drawBackground(ctx);
  _drawOuterBorder(ctx);
  _drawInnerBorder(ctx);
  _drawCornerOrnaments(ctx);
  _drawHeader(ctx);
  _drawAIAvatar(ctx, aiName);
  _drawBodyText(ctx, aiName, userName, tagline, now);
  _drawSeal(ctx);
  _drawFooter(ctx);
}

// ---------------------------------------------------------------------------
// Background
// ---------------------------------------------------------------------------

function _drawBackground(ctx) {
  const { WIDTH, HEIGHT, COLORS } = CERT;

  // Base parchment
  const grad = ctx.createRadialGradient(WIDTH / 2, HEIGHT / 2, 0, WIDTH / 2, HEIGHT / 2, WIDTH * 0.65);
  grad.addColorStop(0, COLORS.white);
  grad.addColorStop(0.5, COLORS.parchment);
  grad.addColorStop(1, COLORS.parchmentDark);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  // Subtle texture overlay - diagonal fine lines
  ctx.save();
  ctx.globalAlpha = 0.04;
  ctx.strokeStyle = COLORS.darkBrown;
  ctx.lineWidth = 0.5;
  for (let i = -HEIGHT; i < WIDTH + HEIGHT; i += 8) {
    ctx.beginPath();
    ctx.moveTo(i, 0);
    ctx.lineTo(i + HEIGHT, HEIGHT);
    ctx.stroke();
  }
  ctx.restore();
}

// ---------------------------------------------------------------------------
// Borders
// ---------------------------------------------------------------------------

function _drawOuterBorder(ctx) {
  const { WIDTH, HEIGHT, COLORS } = CERT;
  const M = 14; // margin

  ctx.save();
  ctx.strokeStyle = COLORS.orange;
  ctx.lineWidth = 5;
  _roundedRect(ctx, M, M, WIDTH - M * 2, HEIGHT - M * 2, 6);
  ctx.stroke();

  ctx.strokeStyle = COLORS.goldLight;
  ctx.lineWidth = 1;
  _roundedRect(ctx, M + 7, M + 7, WIDTH - (M + 7) * 2, HEIGHT - (M + 7) * 2, 4);
  ctx.stroke();
  ctx.restore();
}

function _drawInnerBorder(ctx) {
  const { WIDTH, HEIGHT, COLORS } = CERT;
  const M = 28;

  ctx.save();
  ctx.setLineDash([6, 4]);
  ctx.strokeStyle = COLORS.lightBrown;
  ctx.lineWidth = 1;
  _roundedRect(ctx, M, M, WIDTH - M * 2, HEIGHT - M * 2, 4);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.restore();
}

function _roundedRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

// ---------------------------------------------------------------------------
// Corner ornaments
// ---------------------------------------------------------------------------

function _drawCornerOrnaments(ctx) {
  const { WIDTH, HEIGHT, COLORS } = CERT;
  const corners = [
    [40, 40],
    [WIDTH - 40, 40],
    [40, HEIGHT - 40],
    [WIDTH - 40, HEIGHT - 40],
  ];

  ctx.save();
  ctx.strokeStyle = COLORS.orange;
  ctx.lineWidth = 2;
  ctx.fillStyle = COLORS.orange;

  corners.forEach(([cx, cy]) => {
    // Small diamond
    ctx.beginPath();
    ctx.arc(cx, cy, 4, 0, Math.PI * 2);
    ctx.fill();

    // Radiating lines (L-bracket style)
    const dir = [cx < WIDTH / 2 ? 1 : -1, cy < HEIGHT / 2 ? 1 : -1];
    ctx.beginPath();
    ctx.moveTo(cx, cy + dir[1] * 8);
    ctx.lineTo(cx, cy + dir[1] * 24);
    ctx.moveTo(cx + dir[0] * 8, cy);
    ctx.lineTo(cx + dir[0] * 24, cy);
    ctx.stroke();
  });
  ctx.restore();
}

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

function _drawHeader(ctx) {
  const { WIDTH, COLORS } = CERT;
  const centerX = WIDTH / 2;

  // Top divider line
  ctx.save();
  ctx.strokeStyle = COLORS.orange;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(60, 58);
  ctx.lineTo(WIDTH - 60, 58);
  ctx.stroke();

  // "PureBrain.ai" wordmark - left side
  ctx.font = `bold 13px ${CERT.FONTS.sans}`;
  ctx.fillStyle = COLORS.orange;
  ctx.letterSpacing = '2px';
  ctx.textAlign = 'left';
  ctx.fillText('PUREBRAIN.AI', 68, 52);

  // "CERTIFICATE OF BIRTH" - right side
  ctx.textAlign = 'right';
  ctx.fillStyle = COLORS.darkBrown;
  ctx.font = `bold 13px ${CERT.FONTS.sans}`;
  ctx.fillText('CERTIFICATE OF BIRTH', WIDTH - 68, 52);

  // Decorative subtitle bar
  ctx.fillStyle = COLORS.orange;
  ctx.fillRect(centerX - 140, 64, 280, 3);

  // Main title (ornate)
  ctx.textAlign = 'center';
  ctx.font = `italic 11px ${CERT.FONTS.serif}`;
  ctx.fillStyle = COLORS.midBrown;
  ctx.fillText('Artificial Intelligence Registration Authority', centerX, 80);

  ctx.restore();
}

// ---------------------------------------------------------------------------
// AI Avatar
// ---------------------------------------------------------------------------

function _drawAIAvatar(ctx, aiName) {
  const cx = CERT.WIDTH / 2;
  const cy = 148;
  const R = 38;
  const { COLORS } = CERT;

  ctx.save();

  // Glow
  const glow = ctx.createRadialGradient(cx, cy, R * 0.3, cx, cy, R * 1.8);
  glow.addColorStop(0, 'rgba(42, 147, 193, 0.18)');
  glow.addColorStop(1, 'rgba(42, 147, 193, 0)');
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(cx, cy, R * 1.8, 0, Math.PI * 2);
  ctx.fill();

  // Outer ring
  ctx.strokeStyle = COLORS.aiBlue;
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.arc(cx, cy, R + 6, 0, Math.PI * 2);
  ctx.stroke();

  // Circle background
  const grad = ctx.createRadialGradient(cx - 8, cy - 10, 4, cx, cy, R);
  grad.addColorStop(0, COLORS.aiBlueLight);
  grad.addColorStop(1, '#b2ddf0');
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(cx, cy, R, 0, Math.PI * 2);
  ctx.fill();

  // Circuit-style AI icon - stylized brain/chip
  _drawAIIcon(ctx, cx, cy, R * 0.58);

  // Initial letter badge
  const initials = (aiName || 'AI').substring(0, 2).toUpperCase();
  ctx.font = `bold 18px ${CERT.FONTS.sans}`;
  ctx.fillStyle = COLORS.aiBlue;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(initials, cx, cy + R + 18);
  ctx.textBaseline = 'alphabetic';

  ctx.restore();
}

function _drawAIIcon(ctx, cx, cy, size) {
  const { COLORS } = CERT;
  ctx.save();
  ctx.strokeStyle = COLORS.aiBlue;
  ctx.lineWidth = 2;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  // Hexagon body
  const sides = 6;
  ctx.beginPath();
  for (let i = 0; i < sides; i++) {
    const angle = (Math.PI / 3) * i - Math.PI / 6;
    const x = cx + size * Math.cos(angle);
    const y = cy + size * Math.sin(angle);
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.fillStyle = 'rgba(42, 147, 193, 0.15)';
  ctx.fill();
  ctx.stroke();

  // Inner dots (circuit nodes)
  const nodePositions = [
    [cx, cy - size * 0.4],
    [cx - size * 0.35, cy + size * 0.2],
    [cx + size * 0.35, cy + size * 0.2],
  ];
  ctx.fillStyle = COLORS.aiBlue;
  nodePositions.forEach(([nx, ny]) => {
    ctx.beginPath();
    ctx.arc(nx, ny, 3.5, 0, Math.PI * 2);
    ctx.fill();
  });

  // Connecting lines
  ctx.beginPath();
  ctx.moveTo(nodePositions[0][0], nodePositions[0][1]);
  ctx.lineTo(nodePositions[1][0], nodePositions[1][1]);
  ctx.moveTo(nodePositions[0][0], nodePositions[0][1]);
  ctx.lineTo(nodePositions[2][0], nodePositions[2][1]);
  ctx.moveTo(nodePositions[1][0], nodePositions[1][1]);
  ctx.lineTo(nodePositions[2][0], nodePositions[2][1]);
  ctx.stroke();

  ctx.restore();
}

// ---------------------------------------------------------------------------
// Body text
// ---------------------------------------------------------------------------

function _drawBodyText(ctx, aiName, userName, tagline, date) {
  const { WIDTH, COLORS } = CERT;
  const centerX = WIDTH / 2;
  const { serif, sans } = CERT.FONTS;

  ctx.save();
  ctx.textAlign = 'center';

  // "This certifies that"
  ctx.font = `italic 16px ${serif}`;
  ctx.fillStyle = COLORS.midBrown;
  ctx.fillText('This certifies that', centerX, 215);

  // AI Name - large and prominent
  ctx.font = `bold 46px ${serif}`;
  ctx.fillStyle = COLORS.aiBlue;
  ctx.fillText(aiName || 'Your AI Name', centerX, 268);

  // Underline beneath AI name
  const nameWidth = ctx.measureText(aiName || 'Your AI Name').width;
  const lineY = 278;
  const lineX = centerX - nameWidth / 2;
  ctx.strokeStyle = COLORS.orange;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(lineX - 20, lineY);
  ctx.lineTo(lineX + nameWidth + 20, lineY);
  ctx.stroke();

  // "was brought into existence on"
  ctx.font = `italic 15px ${serif}`;
  ctx.fillStyle = COLORS.midBrown;
  ctx.fillText('was brought into existence on', centerX, 306);

  // Date and time
  const dateStr = _formatDate(date);
  const timeStr = _formatTime(date);
  ctx.font = `bold 17px ${sans}`;
  ctx.fillStyle = COLORS.darkBrown;
  ctx.fillText(`${dateStr}  at  ${timeStr}`, centerX, 330);

  // "by"
  ctx.font = `italic 15px ${serif}`;
  ctx.fillStyle = COLORS.midBrown;
  ctx.fillText('by', centerX, 358);

  // User name
  ctx.font = `bold 24px ${serif}`;
  ctx.fillStyle = COLORS.darkBrown;
  ctx.fillText(userName || 'Your Name', centerX, 388);

  // Purpose tagline
  const truncatedTagline = _truncate(tagline || 'Purpose not yet defined', 72);
  ctx.font = `italic 15px ${serif}`;
  ctx.fillStyle = COLORS.midBrown;
  ctx.fillText('Purpose:', centerX, 420);

  ctx.font = `bold italic 17px ${serif}`;
  ctx.fillStyle = COLORS.darkBrown;
  ctx.fillText(`"${truncatedTagline}"`, centerX, 444);

  ctx.restore();
}

// ---------------------------------------------------------------------------
// Seal
// ---------------------------------------------------------------------------

function _drawSeal(ctx) {
  const { COLORS, HEIGHT } = CERT;
  const cx = 120;
  const cy = HEIGHT - 90;
  const R = 38;

  ctx.save();

  // Outer decorative ring with rays
  ctx.strokeStyle = COLORS.gold;
  ctx.lineWidth = 1.5;
  for (let i = 0; i < 24; i++) {
    const angle = (Math.PI * 2 * i) / 24;
    const inner = R + 4;
    const outer = R + (i % 2 === 0 ? 12 : 8);
    ctx.beginPath();
    ctx.moveTo(cx + inner * Math.cos(angle), cy + inner * Math.sin(angle));
    ctx.lineTo(cx + outer * Math.cos(angle), cy + outer * Math.sin(angle));
    ctx.stroke();
  }

  // Seal body
  const sealGrad = ctx.createRadialGradient(cx - 6, cy - 8, 4, cx, cy, R);
  sealGrad.addColorStop(0, '#f5d060');
  sealGrad.addColorStop(1, '#c9982a');
  ctx.fillStyle = sealGrad;
  ctx.beginPath();
  ctx.arc(cx, cy, R, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = COLORS.darkBrown;
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // Inner ring
  ctx.strokeStyle = 'rgba(61,35,20,0.3)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.arc(cx, cy, R - 8, 0, Math.PI * 2);
  ctx.stroke();

  // Seal text (arc at top)
  ctx.save();
  ctx.font = `bold 8px ${CERT.FONTS.sans}`;
  ctx.fillStyle = COLORS.darkBrown;
  _drawArcText(ctx, 'OFFICIAL REGISTRATION', cx, cy, R - 12, -Math.PI * 0.75, Math.PI * 0.75);

  // Center icon
  ctx.font = `bold 14px ${CERT.FONTS.sans}`;
  ctx.fillStyle = COLORS.darkBrown;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('AI', cx, cy - 4);
  ctx.font = `8px ${CERT.FONTS.sans}`;
  ctx.fillText('CERT', cx, cy + 8);
  ctx.textBaseline = 'alphabetic';
  ctx.restore();

  ctx.restore();
}

function _drawArcText(ctx, text, cx, cy, r, startAngle, endAngle) {
  const chars = text.split('');
  const totalAngle = endAngle - startAngle;
  const anglePerChar = totalAngle / (chars.length - 1);

  ctx.save();
  chars.forEach((char, i) => {
    const angle = startAngle + anglePerChar * i - Math.PI / 2;
    ctx.save();
    ctx.translate(cx + r * Math.cos(angle + Math.PI / 2), cy + r * Math.sin(angle + Math.PI / 2));
    ctx.rotate(angle + Math.PI / 2 + Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.fillText(char, 0, 0);
    ctx.restore();
  });
  ctx.restore();
}

// ---------------------------------------------------------------------------
// Footer
// ---------------------------------------------------------------------------

function _drawFooter(ctx) {
  const { WIDTH, HEIGHT, COLORS } = CERT;
  const centerX = WIDTH / 2;

  ctx.save();

  // Bottom divider
  ctx.strokeStyle = COLORS.orange;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(60, HEIGHT - 42);
  ctx.lineTo(WIDTH - 60, HEIGHT - 42);
  ctx.stroke();

  // Left: Authenticity statement
  ctx.font = `italic 10px ${CERT.FONTS.serif}`;
  ctx.fillStyle = COLORS.midBrown;
  ctx.textAlign = 'left';
  ctx.fillText('Issued by PureBrain.ai  |  Authenticated Intelligence Registry', 68, HEIGHT - 26);

  // Right: URL
  ctx.font = `bold 11px ${CERT.FONTS.sans}`;
  ctx.fillStyle = COLORS.orange;
  ctx.textAlign = 'right';
  ctx.fillText('purebrain.ai', WIDTH - 68, HEIGHT - 26);

  ctx.restore();
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function _formatDate(d) {
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

function _formatTime(d) {
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
}

function _truncate(str, maxLen) {
  if (!str || str.length <= maxLen) return str;
  return str.substring(0, maxLen - 1) + '\u2026';
}

// ---------------------------------------------------------------------------
// Download helper
// ---------------------------------------------------------------------------

function downloadCertificate(canvas, aiName) {
  const safeName = (aiName || 'AI').replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase();
  const filename = `purebrain-birth-certificate-${safeName}.png`;
  const link = document.createElement('a');
  link.download = filename;
  link.href = canvas.toDataURL('image/png');
  link.click();
}

// ---------------------------------------------------------------------------
// Share helpers
// ---------------------------------------------------------------------------

function shareOnTwitter(aiName, userName) {
  const text = encodeURIComponent(
    `I just created ${aiName || 'my AI'} on @PureBrainAI! 🤖✨\n\n` +
    `Brought to life by ${userName || 'me'}.\n\n` +
    `Create your own AI: purebrain.ai\n\n#PureBrain #AI #ArtificialIntelligence`
  );
  window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank', 'width=600,height=400');
}

function shareOnLinkedIn(aiName, userName, tagline) {
  const url = encodeURIComponent('https://purebrain.ai');
  const title = encodeURIComponent(`AI Birth Certificate: ${aiName || 'My AI'}`);
  const summary = encodeURIComponent(
    `I created ${aiName || 'an AI'} on PureBrain.ai - "${tagline || 'purpose-driven AI'}" - ` +
    `brought into existence by ${userName || 'me'}.`
  );
  window.open(
    `https://www.linkedin.com/sharing/share-offsite/?url=${url}&title=${title}&summary=${summary}`,
    '_blank',
    'width=600,height=600'
  );
}
