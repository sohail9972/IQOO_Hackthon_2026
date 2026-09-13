package com.pharmagraph.app.domain

class DrugNormalizerImpl : DrugNormalizer {
    override suspend fun normalize(candidates: List<DrugCandidate>): List<DrugCandidate> {
        // For now, normalization is handled by the Verifier (Stage B) 
        // which populates normalizedName if a trusted match is found.
        // This is a placeholder for future intelligent SLM-based normalization.
        return candidates
    }
}
