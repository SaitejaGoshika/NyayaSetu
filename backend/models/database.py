SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    display_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    owner_uid TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    storage_name TEXT NOT NULL UNIQUE,
    content_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    owner_uid TEXT NOT NULL,
    rules_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    extracted_text TEXT NOT NULL,
    findings_json TEXT NOT NULL,
    UNIQUE(document_id, owner_uid, rules_version)
);

CREATE INDEX IF NOT EXISTS idx_documents_owner_created
ON documents(owner_uid, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_analyses_document_owner
ON analyses(document_id, owner_uid, rules_version);
"""
