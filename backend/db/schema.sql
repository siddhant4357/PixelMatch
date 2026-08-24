-- Users (synced from Clerk)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Selfie embeddings (512-dim ArcFace, stored as BYTEA/JSONB)
CREATE TABLE IF NOT EXISTS user_embeddings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    embedding BYTEA NOT NULL,
    selfie_thumbnail TEXT,
    uploaded_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ
);

-- Rooms/Events
CREATE TABLE IF NOT EXISTS rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_code CHAR(6) UNIQUE NOT NULL,
    event_name TEXT NOT NULL,
    event_date DATE,
    cover_emoji TEXT DEFAULT '📸',
    photo_count INT DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    faiss_index_url TEXT,
    embedding_expires_days INT DEFAULT 7
);

-- Room membership
CREATE TABLE IF NOT EXISTS room_members (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('admin', 'guest')),
    joined_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, room_id)
);

-- Consent records (privacy compliance)
CREATE TABLE IF NOT EXISTS consent_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
    consented_at TIMESTAMPTZ DEFAULT now(),
    purpose TEXT DEFAULT 'photo_search',
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rooms_code ON rooms(room_code);
CREATE INDEX IF NOT EXISTS idx_room_members_user ON room_members(user_id);
CREATE INDEX IF NOT EXISTS idx_room_members_room ON room_members(room_id);
CREATE INDEX IF NOT EXISTS idx_consent_user ON consent_records(user_id);
