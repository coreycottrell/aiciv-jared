/**
 * PureBrain Hub - Express Backend
 * sql.js (pure JS SQLite) + file storage + Google Drive sync stub
 */

import express from 'express'
import fileUpload from 'express-fileupload'
import cors from 'cors'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'
import { v4 as uuidv4 } from 'uuid'
import { execSync } from 'child_process'
import { createRequire } from 'module'

const require = createRequire(import.meta.url)
const initSqlJs = require('sql.js')

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.join(__dirname, '..')
const UPLOADS_DIR = path.join(ROOT, 'uploads')
const DB_PATH = path.join(ROOT, 'hub.db')

// Ensure uploads directory exists
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR, { recursive: true })

// ===== Database Setup (sql.js - pure JS) =====
let db

async function initDB() {
  const SQL = await initSqlJs()

  // Load existing DB if it exists, otherwise create fresh
  if (fs.existsSync(DB_PATH)) {
    const fileBuffer = fs.readFileSync(DB_PATH)
    db = new SQL.Database(fileBuffer)
  } else {
    db = new SQL.Database()
  }

  // Create tables
  db.run(`
    CREATE TABLE IF NOT EXISTS posts (
      id TEXT PRIMARY KEY,
      title TEXT,
      content TEXT NOT NULL,
      author_name TEXT NOT NULL,
      department TEXT,
      tags TEXT DEFAULT '[]',
      is_win INTEGER DEFAULT 0,
      image_url TEXT,
      gdrive_url TEXT,
      created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
      updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
    )
  `)

  db.run(`
    CREATE TABLE IF NOT EXISTS reactions (
      id TEXT PRIMARY KEY,
      post_id TEXT NOT NULL,
      user_name TEXT NOT NULL,
      type TEXT NOT NULL,
      created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
    )
  `)

  db.run(`
    CREATE TABLE IF NOT EXISTS files (
      id TEXT PRIMARY KEY,
      filename TEXT NOT NULL,
      original_name TEXT NOT NULL,
      mime_type TEXT,
      size INTEGER,
      tags TEXT DEFAULT '[]',
      description TEXT,
      uploader_name TEXT NOT NULL,
      gdrive_synced INTEGER DEFAULT 0,
      gdrive_file_id TEXT,
      gdrive_url TEXT,
      created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
    )
  `)

  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      role TEXT DEFAULT 'Member',
      department TEXT,
      token TEXT UNIQUE,
      created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
    )
  `)

  // Seed demo users
  const userCount = db.exec('SELECT COUNT(*) as c FROM users')[0]?.values?.[0]?.[0] || 0
  if (userCount === 0) {
    db.run(`INSERT OR IGNORE INTO users (id, name, role, department, token) VALUES
      ('u1', 'Jared Sanborn', 'Admin', 'Leadership', 'team2025'),
      ('u2', 'Sarah K.', 'Safety Lead', 'Operations', 'safety2025'),
      ('u3', 'Marcus T.', 'Quality Manager', 'Quality', 'quality2025'),
      ('u4', 'Demo User', 'Member', 'General', 'demo')
    `)
  }

  saveDB()
  console.log('  Database initialized (sql.js)')
}

function saveDB() {
  const data = db.export()
  fs.writeFileSync(DB_PATH, Buffer.from(data))
}

// Helper: run query and return all rows as objects
function queryAll(sql, params = []) {
  try {
    const stmt = db.prepare(sql)
    stmt.bind(params)
    const rows = []
    while (stmt.step()) {
      rows.push(stmt.getAsObject())
    }
    stmt.free()
    return rows
  } catch (err) {
    console.error('queryAll error:', sql, err.message)
    return []
  }
}

function queryOne(sql, params = []) {
  const rows = queryAll(sql, params)
  return rows[0] || null
}

function run(sql, params = []) {
  try {
    db.run(sql, params)
    saveDB()
  } catch (err) {
    console.error('run error:', sql, err.message)
    throw err
  }
}

// ===== Express App =====
const app = express()
const PORT = 3001

app.use(cors({ origin: ['http://localhost:5173', 'http://localhost:5174', 'http://localhost:4173'] }))
app.use(express.json())
app.use(fileUpload({
  limits: { fileSize: 50 * 1024 * 1024 },
  createParentPath: true,
}))
app.use('/uploads', express.static(UPLOADS_DIR))

// ===== Auth =====
app.post('/api/auth/login', (req, res) => {
  const { token, name } = req.body
  if (token) {
    const user = queryOne('SELECT * FROM users WHERE token = ?', [token])
    if (user) return res.json({ success: true, user: { name: user.name, role: user.role, department: user.department } })
    return res.status(401).json({ error: 'Invalid token' })
  }
  if (name && name.trim().length >= 2) {
    return res.json({ success: true, user: { name: name.trim(), role: 'Member', department: 'General' } })
  }
  return res.status(400).json({ error: 'Provide token or name' })
})

// ===== Posts =====
app.get('/api/posts', (req, res) => {
  const { wins_only, tag } = req.query
  let posts = queryAll('SELECT * FROM posts ORDER BY created_at DESC')

  if (wins_only === '1') posts = posts.filter(p => p.is_win)
  if (tag) posts = posts.filter(p => {
    try { return JSON.parse(p.tags || '[]').includes(tag) } catch { return false }
  })

  const enriched = posts.map(post => {
    const reactRows = queryAll(
      'SELECT type, COUNT(*) as count FROM reactions WHERE post_id = ? GROUP BY type',
      [post.id]
    )
    const reactions = {}
    reactRows.forEach(r => { reactions[r.type] = Number(r.count) })
    return {
      ...post,
      tags: safeParseJSON(post.tags, []),
      is_win: Boolean(post.is_win),
      reactions,
      userReactions: [],
    }
  })

  res.json(enriched)
})

app.get('/api/posts/:id', (req, res) => {
  const post = queryOne('SELECT * FROM posts WHERE id = ?', [req.params.id])
  if (!post) return res.status(404).json({ error: 'Not found' })
  res.json({ ...post, tags: safeParseJSON(post.tags, []), is_win: Boolean(post.is_win) })
})

app.post('/api/posts', async (req, res) => {
  const { title, content, author_name, department, tags, is_win } = req.body
  if (!content || !author_name) return res.status(400).json({ error: 'content and author_name required' })

  const id = uuidv4()
  let imageUrl = null

  if (req.files?.image) {
    const img = req.files.image
    const ext = path.extname(img.name) || '.jpg'
    const imgName = `${id}${ext}`
    const imgPath = path.join(UPLOADS_DIR, imgName)
    await img.mv(imgPath)
    imageUrl = `/uploads/${imgName}`
  }

  const parsedTags = typeof tags === 'string' ? tags : JSON.stringify(tags || [])
  const isWin = (is_win === 'true' || is_win === true) ? 1 : 0
  const now = new Date().toISOString()

  run(
    'INSERT INTO posts (id, title, content, author_name, department, tags, is_win, image_url, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
    [id, title || null, content, author_name, department || 'General', parsedTags, isWin, imageUrl, now, now]
  )

  const post = queryOne('SELECT * FROM posts WHERE id = ?', [id])
  res.status(201).json({ ...post, tags: safeParseJSON(post.tags, []), is_win: Boolean(post.is_win) })
})

app.post('/api/posts/:id/react', (req, res) => {
  const { type, adding, user_name } = req.body
  const postId = req.params.id
  const userName = user_name || 'anonymous'

  if (adding) {
    // Check for existing reaction first
    const existing = queryOne(
      'SELECT id FROM reactions WHERE post_id = ? AND user_name = ? AND type = ?',
      [postId, userName, type]
    )
    if (!existing) {
      run('INSERT INTO reactions (id, post_id, user_name, type) VALUES (?,?,?,?)',
        [uuidv4(), postId, userName, type])
    }
  } else {
    run('DELETE FROM reactions WHERE post_id = ? AND user_name = ? AND type = ?',
      [postId, userName, type])
  }

  const reactRows = queryAll(
    'SELECT type, COUNT(*) as count FROM reactions WHERE post_id = ? GROUP BY type',
    [postId]
  )
  const reactions = {}
  reactRows.forEach(r => { reactions[r.type] = Number(r.count) })

  res.json({ success: true, reactions })
})

app.delete('/api/posts/:id', (req, res) => {
  run('DELETE FROM posts WHERE id = ?', [req.params.id])
  res.json({ success: true })
})

// ===== Files =====
app.get('/api/files', (req, res) => {
  const { tag } = req.query
  let files = queryAll('SELECT * FROM files ORDER BY created_at DESC')
  if (tag) files = files.filter(f => {
    try { return JSON.parse(f.tags || '[]').includes(tag) } catch { return false }
  })
  res.json(files.map(f => ({ ...f, tags: safeParseJSON(f.tags, []), gdrive_synced: Boolean(f.gdrive_synced) })))
})

app.post('/api/files/upload', async (req, res) => {
  if (!req.files?.file) return res.status(400).json({ error: 'No file provided' })

  const file = req.files.file
  const id = uuidv4()
  const ext = path.extname(file.name)
  const filename = `${id}${ext}`
  const filePath = path.join(UPLOADS_DIR, filename)

  await file.mv(filePath)

  const { tags, description, uploader_name } = req.body
  const parsedTags = typeof tags === 'string' ? tags : JSON.stringify(tags || [])
  const now = new Date().toISOString()

  run(
    'INSERT INTO files (id, filename, original_name, mime_type, size, tags, description, uploader_name, created_at) VALUES (?,?,?,?,?,?,?,?,?)',
    [id, filename, file.name, file.mimetype, file.size, parsedTags, description || null, uploader_name || 'Team Member', now]
  )

  // Fire and forget GDrive sync
  triggerGDriveSync(id, filePath, file.name)

  const dbFile = queryOne('SELECT * FROM files WHERE id = ?', [id])
  res.status(201).json({ ...dbFile, tags: safeParseJSON(dbFile.tags, []), gdrive_synced: false })
})

app.post('/api/files/:id/sync-gdrive', async (req, res) => {
  const file = queryOne('SELECT * FROM files WHERE id = ?', [req.params.id])
  if (!file) return res.status(404).json({ error: 'File not found' })
  const filePath = path.join(UPLOADS_DIR, file.filename)
  const result = await triggerGDriveSync(req.params.id, filePath, file.original_name)
  res.json(result)
})

app.get('/api/files/:id/download', (req, res) => {
  const file = queryOne('SELECT * FROM files WHERE id = ?', [req.params.id])
  if (!file) return res.status(404).json({ error: 'Not found' })
  const filePath = path.join(UPLOADS_DIR, file.filename)
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'File missing from disk' })
  res.download(filePath, file.original_name)
})

app.delete('/api/files/:id', (req, res) => {
  const file = queryOne('SELECT * FROM files WHERE id = ?', [req.params.id])
  if (file) {
    const filePath = path.join(UPLOADS_DIR, file.filename)
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath)
    run('DELETE FROM files WHERE id = ?', [req.params.id])
  }
  res.json({ success: true })
})

// ===== Google Drive Integration =====
const GDRIVE_MANAGER = '/home/jared/projects/AI-CIV/aether/tools/gdrive_manager.py'
const HUB_FOLDER_NAME = 'PureBrain Hub Files'

async function triggerGDriveSync(fileId, localPath, originalName) {
  try {
    if (!fs.existsSync(GDRIVE_MANAGER)) {
      console.log(`[GDrive] Stub mode - simulating sync for ${originalName}`)
      setTimeout(() => {
        try {
          run('UPDATE files SET gdrive_synced = 1, gdrive_url = ? WHERE id = ?',
            ['https://drive.google.com/drive/folders/purebrain-hub-stub', fileId])
          console.log(`[GDrive] Stub sync complete for ${fileId}`)
        } catch (e) { console.error('[GDrive] Stub update error:', e.message) }
      }, 2500)
      return { success: true, stub: true }
    }

    const cmd = `python3 "${GDRIVE_MANAGER}" upload "${localPath}" 2>&1`
    console.log(`[GDrive] Running: ${cmd}`)
    const output = execSync(cmd, { timeout: 30000, encoding: 'utf8' })

    let gdriveUrl = null
    try {
      const lines = output.trim().split('\n')
      const parsed = JSON.parse(lines[lines.length - 1])
      gdriveUrl = parsed.webViewLink || parsed.url
    } catch {
      const match = output.match(/https:\/\/drive\.google\.com\/[^\s]+/)
      if (match) gdriveUrl = match[0]
    }

    run('UPDATE files SET gdrive_synced = 1, gdrive_url = ? WHERE id = ?',
      [gdriveUrl || 'https://drive.google.com', fileId])

    return { success: true, gdrive_url: gdriveUrl }
  } catch (err) {
    console.error(`[GDrive] Sync error for ${fileId}:`, err.message)
    return { success: false, error: err.message }
  }
}

// ===== GDrive Status =====
app.get('/api/gdrive/status', (req, res) => {
  const syncedCount = queryOne('SELECT COUNT(*) as c FROM files WHERE gdrive_synced = 1')
  res.json({
    connected: true,
    real_gdrive: fs.existsSync(GDRIVE_MANAGER),
    folder_name: HUB_FOLDER_NAME,
    last_sync: new Date().toISOString(),
    files_synced: syncedCount?.c || 0,
  })
})

app.post('/api/gdrive/sync-all', async (req, res) => {
  const unsynced = queryAll('SELECT * FROM files WHERE gdrive_synced = 0')
  const results = []
  for (const file of unsynced) {
    const filePath = path.join(UPLOADS_DIR, file.filename)
    const result = await triggerGDriveSync(file.id, filePath, file.original_name)
    results.push({ file_id: file.id, ...result })
  }
  res.json({
    synced: results.filter(r => r.success).length,
    failed: results.filter(r => !r.success).length,
    files: results
  })
})

// ===== Health Check =====
app.get('/api/health', (req, res) => {
  const postCount = queryOne('SELECT COUNT(*) as c FROM posts')
  const fileCount = queryOne('SELECT COUNT(*) as c FROM files')
  res.json({
    status: 'ok',
    db: 'sql.js',
    posts: postCount?.c || 0,
    files: fileCount?.c || 0,
    uptime: process.uptime(),
  })
})

// ===== Helpers =====
function safeParseJSON(str, fallback = null) {
  try { return JSON.parse(str) } catch { return fallback }
}

// ===== Start =====
initDB().then(() => {
  app.listen(PORT, () => {
    console.log(`\n  PureBrain Hub Backend`)
    console.log(`  Running on: http://localhost:${PORT}`)
    console.log(`  Database:   ${DB_PATH}`)
    console.log(`  Uploads:    ${UPLOADS_DIR}`)
    console.log(`  GDrive:     ${fs.existsSync(GDRIVE_MANAGER) ? 'Connected (real)' : 'Stub mode'}`)
    console.log('')
  })
}).catch(err => {
  console.error('Failed to initialize DB:', err)
  process.exit(1)
})
