package com.pharmagraph.app.logic

import com.pharmagraph.app.domain.DrugCandidate
import com.pharmagraph.app.domain.DrugExtractor
import com.pharmagraph.app.domain.VerificationStatus

class StageADrugExtractor : DrugExtractor {

    private val DRUG_PREFIXES = listOf("tab", "cap", "syp", "inj", "rx", "t")

    private val DOSAGE_PATTERN = Regex(
        """(\d+(?:\.\d+)?)\s*(mg|ml|g|tab)\b""",
        RegexOption.IGNORE_CASE
    )

    private val FREQ_PATTERN = Regex(
        """\b(\d-\d-\d|\d-\d|OD|BD|TDS)\b""",
        RegexOption.IGNORE_CASE
    )

    private val SKIP_WORDS = listOf(
        "figure", "patient", "address", "date",
        "doctor", "hospital", "clinic", "signature"
    )

    override suspend fun extractDrugs(ocrText: String): List<DrugCandidate> {
        val candidates = mutableListOf<DrugCandidate>()

        for (line in ocrText.split("\n", "\r\n")) {
            val trimmed = line.trim()
            if (trimmed.length < 3 || trimmed.length > 100) continue
            if (shouldSkip(trimmed)) continue

            val candidate = extractFromLine(trimmed)
            if (candidate != null) candidates.add(candidate)
        }

        return candidates.distinctBy { it.rawName.lowercase() }
    }

    private fun shouldSkip(line: String): Boolean {
        val lower = line.lowercase()
        if (lower.contains("http") || lower.contains(".com") ||
            lower.contains(".net") || lower.contains("www.")) return true
        if (SKIP_WORDS.any { lower.contains(it) }) return true
        return line.count { it.isLetter() } < 3
    }

    private fun extractFromLine(line: String): DrugCandidate? {
        val lower = line.lowercase()

        val hasPrefix = DRUG_PREFIXES.any {
            lower.startsWith("$it ") || lower.startsWith("$it.")
        }
        if (hasPrefix) {
            val parts = line.split(" ", limit = 2)
            if (parts.size < 2) return null
            val name = parts[1].takeWhile { it.isLetter() || it == '-' || it == ' ' }
                .trim().split(" ").firstOrNull() ?: return null
            if (name.length < 3) return null
            return candidate(name, line, "after prefix")
        }

        if (DOSAGE_PATTERN.containsMatchIn(line)) {
            val match = DOSAGE_PATTERN.find(line) ?: return null
            val name = line.substring(0, match.range.first)
                .replace(Regex("""^(tab|cap|syp|inj|t)\.?\s+""", RegexOption.IGNORE_CASE), "")
                .trim()
            if (name.length in 3..30) return candidate(name, line, "before dosage")
        }

        if (FREQ_PATTERN.containsMatchIn(line)) {
            val match = FREQ_PATTERN.find(line) ?: return null
            val name = line.substring(0, match.range.first)
                .replace(Regex("""^(tab|cap|syp|inj|t)\.?\s+""", RegexOption.IGNORE_CASE), "")
                .trim()
            if (name.length in 3..30) return candidate(name, line, "before frequency")
        }

        return null
    }

    private fun candidate(name: String, source: String, reason: String) = DrugCandidate(
        rawName = name,
        normalizedName = name,
        confidence = 0.7f,
        verificationStatus = VerificationStatus.YELLOW,
        sourceText = source,
        possibleMatches = emptyList(),
        reason = reason
    )
}