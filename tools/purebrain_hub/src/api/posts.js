/**
 * Posts API - CRUD for team posts/stories
 * Backend: Express + SQLite via /api/posts
 */

const BASE = '/api'

export async function fetchPosts(params = {}) {
  const query = new URLSearchParams(params).toString()
  const res = await fetch(`${BASE}/posts${query ? '?' + query : ''}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function getPost(id) {
  const res = await fetch(`${BASE}/posts/${id}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function createPost(formData) {
  const res = await fetch(`${BASE}/posts`, {
    method: 'POST',
    body: formData, // FormData handles multipart automatically
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: 'Unknown error' }))
    throw new Error(err.error || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function reactToPost(postId, reactionType, adding, userName) {
  const res = await fetch(`${BASE}/posts/${postId}/react`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: reactionType, adding, user_name: userName }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function deletePost(id) {
  const res = await fetch(`${BASE}/posts/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
