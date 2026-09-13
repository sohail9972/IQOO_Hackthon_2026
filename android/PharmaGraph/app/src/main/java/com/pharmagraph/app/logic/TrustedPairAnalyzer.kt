package com.pharmagraph.app.logic

import com.pharmagraph.app.domain.DrugCandidate
import java.util.Locale

enum class RiskLevel {
    DANGER,
    HIGH_RISK,
    MODERATE,
    SAFE
}

data class AnalysisResult(
    val riskLevel: RiskLevel,
    val findings: List<String>,
    val warningText: String
)

class TrustedPairAnalyzer {

    private val dangerousPairs = mapOf(
        Pair("warfarin", "aspirin") to "Severe bleeding",
        Pair("warfarin", "ibuprofen") to "Severe bleeding",
        Pair("aspirin", "ibuprofen") to "GI bleeding",
        Pair("paracetamol", "paracetamol") to "Liver toxicity",
        Pair("codeine", "promethazine") to "Respiratory depression",
        Pair("metformin", "alcohol") to "Lactic acidosis",
        Pair("lithium", "ibuprofen") to "Lithium toxicity",
        Pair("allopurinol", "mercaptopurine") to "Bone marrow suppression",
        Pair("digoxin", "amiodarone") to "Digoxin toxicity",
        Pair("tramadol", "fluoxetine") to "Serotonin syndrome",
        Pair("clopidogrel", "omeprazole") to "Reduced efficacy",
        Pair("atorvastatin", "clarithromycin") to "Rhabdomyolysis"
    )

    fun analyze(
        drugs: List<DrugCandidate>,
        language: String
    ): AnalysisResult {

        val findings = mutableListOf<String>()

        /*
         * Only analyze candidates that have a verified,
         * non-null and non-blank normalized drug name.
         *
         * We intentionally do NOT use !! because normalizedName
         * is nullable and an unverified candidate is valid in
         * the Phase 1 pipeline.
         */
        val names = drugs
            .mapNotNull { candidate ->
                candidate.normalizedName
                    ?.trim()
                    ?.takeIf { it.isNotBlank() }
                    ?.lowercase(Locale.ROOT)
            }

        for (i in names.indices) {
            for (j in i + 1 until names.size) {

                val a = names[i]
                val b = names[j]

                val effect =
                    dangerousPairs[Pair(a, b)]
                        ?: dangerousPairs[Pair(b, a)]

                if (effect != null) {
                    findings.add("$a + $b: $effect")
                }
            }
        }

        val riskLevel: RiskLevel = when {
            findings.isEmpty() -> RiskLevel.SAFE

            findings.any {
                it.contains("Severe", ignoreCase = true) ||
                        it.contains("toxicity", ignoreCase = true) ||
                        it.contains("depression", ignoreCase = true) ||
                        it.contains("Rhabdomyolysis", ignoreCase = true)
            } -> RiskLevel.DANGER

            else -> RiskLevel.HIGH_RISK
        }

        val findingText = findings.joinToString("; ")

        val warningText = when (language) {

            "ta" -> when (riskLevel) {

                RiskLevel.DANGER ->
                    "DANGER. $findingText. Do not take together. Call your doctor."

                RiskLevel.HIGH_RISK ->
                    "HIGH RISK. $findingText. Contact your doctor."

                RiskLevel.MODERATE ->
                    "MODERATE RISK. $findingText. Monitor for symptoms."

                RiskLevel.SAFE ->
                    "SAFE. Take as prescribed."
            }

            "hi" -> when (riskLevel) {

                RiskLevel.DANGER ->
                    "KHATRA. $findingText. Na le. Doctor ko call karein."

                RiskLevel.HIGH_RISK ->
                    "UCCH JOKHIM. $findingText. Doctor se sampark karein."

                RiskLevel.MODERATE ->
                    "MADHYAM JOKHIM. $findingText. Nigrani karein."

                RiskLevel.SAFE ->
                    "SURAKSHIT. Doctor ke anusar lein."
            }

            else -> when (riskLevel) {

                RiskLevel.DANGER ->
                    "DANGER. $findingText. Do not take together. Call your doctor immediately."

                RiskLevel.HIGH_RISK ->
                    "HIGH RISK. $findingText. Contact your doctor."

                RiskLevel.MODERATE ->
                    "MODERATE RISK. $findingText. Monitor for symptoms."

                RiskLevel.SAFE ->
                    "SAFE. Take as prescribed."
            }
        }

        return AnalysisResult(
            riskLevel = riskLevel,
            findings = findings,
            warningText = warningText
        )
    }
}