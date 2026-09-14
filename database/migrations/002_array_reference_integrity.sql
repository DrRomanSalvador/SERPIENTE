-- PostgreSQL foreign keys cannot enforce element-wise references from uuid[]
-- to uuid. These triggers preserve the existing array-based schema while
-- failing closed when an array contains an unknown identifier.

CREATE OR REPLACE FUNCTION validate_uuid_array_references()
RETURNS trigger AS $$
DECLARE
    missing_count INTEGER;
BEGIN
    EXECUTE format(
        'SELECT count(*)
           FROM unnest(COALESCE(($1).%I, ARRAY[]::uuid[])) AS ids(id)
           LEFT JOIN %I target ON target.id = ids.id
          WHERE target.id IS NULL',
        TG_ARGV[1],
        TG_ARGV[0]
    ) INTO missing_count USING NEW;

    IF missing_count > 0 THEN
        RAISE EXCEPTION 'referential integrity violation: %.% contains % unknown UUID reference(s)', TG_TABLE_NAME, TG_ARGV[1], missing_count;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validate_evidences_observations
BEFORE INSERT OR UPDATE OF observation_ids ON evidences
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('observations', 'observation_ids');

CREATE TRIGGER validate_claims_evidence
BEFORE INSERT OR UPDATE OF supporting_evidence_ids, contradicting_evidence_ids ON claims
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('evidences', 'supporting_evidence_ids');

CREATE TRIGGER validate_claims_sources
BEFORE INSERT OR UPDATE OF source_ids ON claims
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('sources', 'source_ids');

CREATE TRIGGER validate_claims_documents
BEFORE INSERT OR UPDATE OF document_ids ON claims
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('documents', 'document_ids');

CREATE TRIGGER validate_hypotheses_evidence
BEFORE INSERT OR UPDATE OF supporting_evidence_ids, contradicting_evidence_ids ON hypotheses
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('evidences', 'supporting_evidence_ids');

CREATE TRIGGER validate_hypotheses_claims
BEFORE INSERT OR UPDATE OF explains_claim_ids ON hypotheses
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('claims', 'explains_claim_ids');

CREATE TRIGGER validate_signals_observations
BEFORE INSERT OR UPDATE OF observation_ids ON signals
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('observations', 'observation_ids');

CREATE TRIGGER validate_signals_evidence
BEFORE INSERT OR UPDATE OF evidence_ids ON signals
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('evidences', 'evidence_ids');

CREATE TRIGGER validate_risks_evidence
BEFORE INSERT OR UPDATE OF evidence_ids ON risk_assessments
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('evidences', 'evidence_ids');

CREATE TRIGGER validate_risks_signals
BEFORE INSERT OR UPDATE OF signal_ids ON risk_assessments
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('signals', 'signal_ids');

CREATE TRIGGER validate_risks_anomalies
BEFORE INSERT OR UPDATE OF anomaly_ids ON risk_assessments
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('anomalies', 'anomaly_ids');

CREATE TRIGGER validate_risks_hypotheses
BEFORE INSERT OR UPDATE OF hypothesis_ids ON risk_assessments
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('hypotheses', 'hypothesis_ids');

CREATE TRIGGER validate_risk_convergences
BEFORE INSERT OR UPDATE OF risk_assessment_ids ON risk_convergences
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('risk_assessments', 'risk_assessment_ids');

CREATE TRIGGER validate_alert_risks
BEFORE INSERT OR UPDATE OF risk_assessment_ids ON alerts
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('risk_assessments', 'risk_assessment_ids');

CREATE TRIGGER validate_alert_convergences
BEFORE INSERT OR UPDATE OF convergence_ids ON alerts
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('risk_convergences', 'convergence_ids');

CREATE TRIGGER validate_alert_anomalies
BEFORE INSERT OR UPDATE OF anomaly_ids ON alerts
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('anomalies', 'anomaly_ids');

CREATE TRIGGER validate_alert_signals
BEFORE INSERT OR UPDATE OF signal_ids ON alerts
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('signals', 'signal_ids');

CREATE TRIGGER validate_scenarios_risks
BEFORE INSERT OR UPDATE OF risk_assessment_ids ON scenarios
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('risk_assessments', 'risk_assessment_ids');

CREATE TRIGGER validate_scenarios_hypotheses
BEFORE INSERT OR UPDATE OF hypothesis_ids ON scenarios
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('hypotheses', 'hypothesis_ids');

CREATE TRIGGER validate_scenarios_signals
BEFORE INSERT OR UPDATE OF signal_ids ON scenarios
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('signals', 'signal_ids');

CREATE TRIGGER validate_interventions_alerts
BEFORE INSERT OR UPDATE OF alert_ids ON interventions
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('alerts', 'alert_ids');

CREATE TRIGGER validate_interventions_risks
BEFORE INSERT OR UPDATE OF risk_assessment_ids ON interventions
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('risk_assessments', 'risk_assessment_ids');
