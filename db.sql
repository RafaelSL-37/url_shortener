CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    type VARCHAR(50) DEFAULT 'DEFAULT' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS urls (
    short_url VARCHAR(10) PRIMARY KEY,
    long_url VARCHAR(2048) NOT NULL,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    clicks INTEGER DEFAULT 0,
    expiration_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer_id ON customers(id);
CREATE INDEX idx_short_url ON urls(short_url);