CREATE TRIGGER validate_claims_contradicting_evidence
BEFORE INSERT OR UPDATE OF contradicting_evidence_ids ON claims
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('evidences', 'contradicting_evidence_ids');

CREATE TRIGGER validate_hypotheses_contradicting_evidence
BEFORE INSERT OR UPDATE OF contradicting_evidence_ids ON hypotheses
FOR EACH ROW EXECUTE FUNCTION validate_uuid_array_references('evidences', 'contradicting_evidence_ids');
