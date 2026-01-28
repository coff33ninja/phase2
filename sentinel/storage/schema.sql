-- System metrics database schema
-- Time-series data storage for all collected metrics

-- System snapshots table (main table)
CREATE TABLE IF NOT EXISTS system_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON system_snapshots(timestamp);

-- CPU metrics
CREATE TABLE IF NOT EXISTS cpu_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    usage_percent REAL NOT NULL,
    frequency_mhz REAL NOT NULL,
    temperature_celsius REAL,
    FOREIGN KEY (snapshot_id) REFERENCES system_snapshots(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cpu_snapshot ON cpu_metrics(snapshot_id);

-- CPU per-core usage
CREATE TABLE IF NOT EXISTS cpu_core_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpu_metric_id INTEGER NOT NULL,
    core_index INTEGER NOT NULL,
    usage_percent REAL NOT NULL,
    FOREIGN KEY (cpu_metric_id) REFERENCES cpu_metrics(id) ON DELETE CASCADE
);

-- RAM metrics
CREATE TABLE IF NOT EXISTS ram_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    total_gb REAL NOT NULL,
    used_gb REAL NOT NULL,
    available_gb REAL NOT NULL,
    cached_gb REAL,
    usage_percent REAL NOT NULL,
    FOREIGN KEY (snapshot_id) REFERENCES system_snapshots(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ram_snapshot ON ram_metrics(snapshot_id);

-- GPU metrics
CREATE TABLE IF NOT EXISTS gpu_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    usage_percent REAL NOT NULL,
    memory_used_gb REAL NOT NULL,
    memory_total_gb REAL NOT NULL,
    temperature_celsius REAL,
    power_draw_watts REAL,
    FOREIGN KEY (snapshot_id) REFERENCES system_snapshots(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_gpu_snapshot ON gpu_metrics(snapshot_id);

-- Disk metrics
CREATE TABLE IF NOT EXISTS disk_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    read_mbps REAL NOT NULL,
    write_mbps REAL NOT NULL,
    queue_length INTEGER NOT NULL,
    usage_percent REAL,
    FOREIGN KEY (snapshot_id) REFERENCES system_snapshots(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_disk_snapshot ON disk_metrics(snapshot_id);

-- Network metrics
CREATE TABLE IF NOT EXISTS network_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    download_mbps REAL NOT NULL,
    upload_mbps REAL NOT NULL,
    connections_active INTEGER NOT NULL,
    FOREIGN KEY (snapshot_id) REFERENCES system_snapshots(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_network_snapshot ON network_metrics(snapshot_id);

-- Process information
CREATE TABLE IF NOT EXISTS process_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    pid INTEGER NOT NULL,
    cpu_percent REAL NOT NULL,
    memory_mb REAL NOT NULL,
    threads INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (snapshot_id) REFERENCES system_snapshots(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_process_snapshot ON process_info(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_process_name ON process_info(name);

-- System context
CREATE TABLE IF NOT EXISTS system_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    user_active BOOLEAN NOT NULL,
    time_of_day TEXT NOT NULL,
    day_of_week TEXT NOT NULL,
    user_action TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES system_snapshots(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_context_snapshot ON system_context(snapshot_id);

-- Anomaly detection results
CREATE TABLE IF NOT EXISTS anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    metric_name TEXT NOT NULL,
    current_value REAL NOT NULL,
    expected_value REAL NOT NULL,
    deviation_std REAL NOT NULL,
    severity TEXT NOT NULL,
    context_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);

-- Metadata table for schema versioning
CREATE TABLE IF NOT EXISTS schema_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_metadata (key, value) VALUES ('version', '1.0.0');
INSERT OR IGNORE INTO schema_metadata (key, value) VALUES ('created_at', datetime('now'));
