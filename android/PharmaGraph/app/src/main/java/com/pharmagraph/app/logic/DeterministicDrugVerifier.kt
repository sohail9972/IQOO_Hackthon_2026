package com.pharmagraph.app.logic

import com.pharmagraph.app.domain.DrugCandidate
import com.pharmagraph.app.domain.DrugVerifier
import com.pharmagraph.app.domain.VerificationStatus

class DeterministicDrugVerifier : DrugVerifier {
    
    // Initial trusted dictionary based on dangerousPairs in MainActivity and common medications
    private val trustedDrugs = setOf(
        "Aspirin", "Warfarin", "Ibuprofen", "Paracetamol", "Codeine", 
        "Promethazine", "Metformin", "Atorvastatin", "Amlodipine", "Lisinopril",
        "Dolo", "Crocin", "Calpol", "Augmentin", "Azithromycin"
    )

    override suspend fun verify(candidates: List<DrugCandidate>, rawOcrText: String): List<DrugCandidate> {
        return candidates.map { candidate ->
            val normalized = candidate.rawName.trim().lowercase()
            val exactMatch = trustedDrugs.find { it.lowercase() == normalized }
            
            val appearsInSource = rawOcrText.contains(candidate.rawName, ignoreCase = true)
            
            if (exactMatch != null && appearsInSource) {
                candidate.copy(
                    normalizedName = exactMatch,
                    verificationStatus = VerificationStatus.GREEN,
                    confidence = 1.0f,
                    reason = "Exact trusted match found."
                )
            } else if (appearsInSource) {
                val fuzzyMatch = findFuzzyMatch(normalized)
                if (fuzzyMatch != null) {
                    candidate.copy(
                        normalizedName = fuzzyMatch,
                        verificationStatus = VerificationStatus.YELLOW,
                        confidence = 0.7f,
                        possibleMatches = listOf(fuzzyMatch),
                        reason = "Possible spelling variation of $fuzzyMatch."
                    )
                } else {
                    candidate.copy(
                        verificationStatus = VerificationStatus.RED,
                        reason = "No trusted match found in dictionary."
                    )
                }
            } else {
                candidate.copy(
                    verificationStatus = VerificationStatus.RED,
                    reason = "Candidate not found in raw prescription text."
                )
            }
        }
    }

    private fun findFuzzyMatch(name: String): String? {
        // Simple heuristic: distance <= 2 for words >= 5 chars, else 1
        val maxDist = if (name.length >= 5) 2 else 1
        return trustedDrugs.find { trusted ->
            levenshteinDistance(name, trusted.lowercase()) <= maxDist
        }
    }

    private fun levenshteinDistance(s1: String, s2: String): Int {
        val dp = Array(s1.length + 1) { IntArray(s2.length + 1) }
        for (i in 0..s1.length) dp[i][0] = i
        for (j in 0..s2.length) dp[0][j] = j
        for (i in 1..s1.length) {
            for (j in 1..s2.length) {
                val cost = if (s1[i - 1] == s2[j - 1]) 0 else 1
                dp[i][j] = minOf(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
            }
        }
        return dp[s1.length][s2.length]
    }
}
