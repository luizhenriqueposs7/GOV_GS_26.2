DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'zelabairro_runtime') THEN
        CREATE ROLE zelabairro_runtime NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
END $$;

GRANT USAGE ON SCHEMA citizentech TO zelabairro_runtime;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA citizentech TO zelabairro_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA citizentech TO zelabairro_runtime;

CREATE POLICY servidor_central ON citizentech.atendimentos TO zelabairro_runtime USING (true) WITH CHECK (true);
CREATE POLICY servidor_central ON citizentech.eventos TO zelabairro_runtime USING (true) WITH CHECK (true);
CREATE POLICY servidor_central ON citizentech.envios TO zelabairro_runtime USING (true) WITH CHECK (true);
CREATE POLICY servidor_central ON citizentech.planos_passagem TO zelabairro_runtime USING (true) WITH CHECK (true);
CREATE POLICY servidor_central ON citizentech.relatos TO zelabairro_runtime USING (true) WITH CHECK (true);
