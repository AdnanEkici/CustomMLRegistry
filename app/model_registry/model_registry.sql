-- Create the model_metadata table
CREATE TABLE IF NOT EXISTS model_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    file_path TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    framework TEXT,
    framework_version TEXT,
    training_data TEXT,
    hyperparameters TEXT,
    evaluation_metrics TEXT,
    model_author TEXT,
    last_updated TEXT,
    uploaded_file_name TEXT,
    features TEXT,
    status TEXT CHECK(status IN ('deployed', 'archived', 'under review')) DEFAULT 'under review',
    UNIQUE(name, version)  -- Ensure unique combination of name and version
);

-- Create the labels table
CREATE TABLE IF NOT EXISTS labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT UNIQUE NOT NULL
);

-- Create the model_labels table
CREATE TABLE IF NOT EXISTS model_labels (
    model_id INTEGER,
    label_id INTEGER,
    FOREIGN KEY (model_id) REFERENCES model_metadata(id) ON DELETE CASCADE,
    FOREIGN KEY (label_id) REFERENCES labels(id) ON DELETE CASCADE,
    PRIMARY KEY (model_id, label_id)
);

-- Insert model metadata
INSERT INTO model_metadata (name, version, file_path, description, created_at, framework, framework_version, training_data, hyperparameters, evaluation_metrics, model_author, last_updated, uploaded_file_name, features, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);

-- Insert label if it does not exist
INSERT OR IGNORE INTO labels (label) VALUES (?);

-- Select label id by label name
SELECT id FROM labels WHERE label = ?;

-- Insert model-label relationship
INSERT INTO model_labels (model_id, label_id) VALUES (?, ?);

-- Select model by name and version
SELECT * FROM model_metadata WHERE name = ? AND version = ?;

-- Select all models
SELECT * FROM model_metadata;

-- Select labels for a given model
SELECT l.label FROM labels l
JOIN model_labels ml ON l.id = ml.label_id
WHERE ml.model_id = ?;

-- Update a model's metadata
UPDATE model_metadata
SET file_path = ?, description = ?, framework = ?, framework_version = ?, training_data = ?, hyperparameters = ?, evaluation_metrics = ?, model_author = ?, last_updated = ?, status = ?
WHERE name = ? AND version = ?;

-- Delete a model by name and version
DELETE FROM model_metadata WHERE name = ? AND version = ?;

DELETE FROM model_labels WHERE model_id = ?;

-- Select model id by name and version
SELECT id FROM model_metadata WHERE name = ? AND version = ?;

-- Delete labels for a given model
DELETE FROM model_labels WHERE model_id = ?;

-- Insert label if it does not exist
INSERT OR IGNORE INTO labels (label) VALUES (?);

-- Select label id by label name
SELECT id FROM labels WHERE label = ?;

--- Select model id by name and version
SELECT id FROM model_metadata WHERE name = ? AND version = ?;

--- Delete labels for a given model':
DELETE FROM model_labels WHERE model_id = ?;

--- Delete a model by name and version':
DELETE FROM model_metadata WHERE name = ? AND version = ?;
