-- =============================================================
-- Darwin — PostgreSQL Initialization Script
-- Audit trail para ciclos de evolução, patches e avaliações.
-- =============================================================

-- Tabela principal: cada ciclo de evolução completo
CREATE TABLE IF NOT EXISTS cycles (
    cycle_id    UUID PRIMARY KEY,
    state       VARCHAR(50)  NOT NULL DEFAULT 'received',

    -- Hotspot que originou o ciclo
    hotspot_type      VARCHAR(50),
    hotspot_endpoint  VARCHAR(255),
    hotspot_instance  VARCHAR(255),
    hotspot_value     DOUBLE PRECISION,
    hotspot_threshold DOUBLE PRECISION,

    -- Patch gerado
    patch_branch  VARCHAR(255),
    patch_file    TEXT,
    rule_applied  VARCHAR(100),

    -- Métricas comparadas
    baseline_metrics  JSONB,
    candidate_metrics JSONB,

    -- Resultado da avaliação
    score          DOUBLE PRECISION,
    recommendation VARCHAR(50),

    -- Diagnóstico em caso de falha
    error TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cycles_state      ON cycles(state);
CREATE INDEX IF NOT EXISTS idx_cycles_created_at ON cycles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cycles_hotspot    ON cycles(hotspot_type, hotspot_endpoint);

-- Tabela: patches gerados (um por ciclo em Onda 1, N no futuro)
CREATE TABLE IF NOT EXISTS patches (
    id           SERIAL  PRIMARY KEY,
    cycle_id     UUID    REFERENCES cycles(cycle_id) ON DELETE CASCADE,
    branch_name  VARCHAR(255) NOT NULL,
    file_path    TEXT,
    rule_applied VARCHAR(100),
    diff         TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patches_cycle ON patches(cycle_id);

-- Tabela: resultado detalhado de cada avaliação
CREATE TABLE IF NOT EXISTS evaluations (
    id               SERIAL  PRIMARY KEY,
    cycle_id         UUID    REFERENCES cycles(cycle_id) ON DELETE CASCADE,
    score            DOUBLE PRECISION NOT NULL,
    recommendation   VARCHAR(50)      NOT NULL,
    confidence       DOUBLE PRECISION,
    delta_latency_pct DOUBLE PRECISION,
    delta_error_pct   DOUBLE PRECISION,
    delta_cpu_pct     DOUBLE PRECISION,
    baseline_metrics  JSONB,
    candidate_metrics JSONB,
    report            JSONB,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluations_cycle ON evaluations(cycle_id);

-- Trigger para manter updated_at atualizado automaticamente
CREATE OR REPLACE FUNCTION _update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_cycles_updated_at ON cycles;
CREATE TRIGGER trg_cycles_updated_at
    BEFORE UPDATE ON cycles
    FOR EACH ROW EXECUTE FUNCTION _update_updated_at();
