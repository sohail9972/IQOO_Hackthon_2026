package com.pharmagraph.app

import android.graphics.Bitmap
import com.pharmagraph.app.domain.*
import com.pharmagraph.app.logic.DeterministicDrugVerifier
import com.pharmagraph.app.logic.PrescriptionAnalysisPipeline
import com.pharmagraph.app.logic.StageADrugExtractor
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.mockito.Mockito.mock

class PrescriptionPipelineTest {

    private val drugExtractor = StageADrugExtractor()
    private val drugVerifier = DeterministicDrugVerifier()
    
    // Mock extractor to provide raw text without real OCR
    private val mockTextExtractor = object : PrescriptionTextExtractor {
        var textToReturn = ""
        override suspend fun extract(image: Bitmap): String = textToReturn
    }

    private val pipeline = PrescriptionAnalysisPipeline(
        mockTextExtractor,
        drugExtractor,
        drugVerifier
    )

    @Test
    fun testExactDrugMatch() = runBlocking {
        mockTextExtractor.textToReturn = "Tab Aspirin 75mg"
        val result = pipeline.process(mock(Bitmap::class.java))
        
        val drug = result.verifiedDrugs.find { it.normalizedName == "Aspirin" }
        assertEquals(VerificationStatus.GREEN, drug?.verificationStatus)
        assertEquals("Aspirin", drug?.normalizedName)
    }

    @Test
    fun testOcrSpellingVariation() = runBlocking {
        // "Asparin" should match "Aspirin" as YELLOW
        mockTextExtractor.textToReturn = "Tab Asparin 75mg"
        val result = pipeline.process(mock(Bitmap::class.java))
        
        val drug = result.verifiedDrugs.find { it.rawName == "Asparin" }
        assertEquals(VerificationStatus.YELLOW, drug?.verificationStatus)
        assertEquals("Aspirin", drug?.normalizedName)
    }

    @Test
    fun testUnknownDrug() = runBlocking {
        mockTextExtractor.textToReturn = "Xyzabc123"
        val result = pipeline.process(mock(Bitmap::class.java))
        
        val drug = result.verifiedDrugs.find { it.rawName == "Xyzabc123" }
        assertEquals(VerificationStatus.RED, drug?.verificationStatus)
    }

    @Test
    fun testMixedPrescriptionText() = runBlocking {
        mockTextExtractor.textToReturn = """
            Tab Aspirin 75mg
            Tab Dolo 650
            1-0-1
        """.trimIndent()
        
        val result = pipeline.process(mock(Bitmap::class.java))
        
        assertTrue(result.verifiedDrugs.any { it.normalizedName == "Aspirin" })
        assertTrue(result.verifiedDrugs.any { it.normalizedName == "Dolo" })
    }

    @Test
    fun testCaseDifferences() = runBlocking {
        mockTextExtractor.textToReturn = "ASPIRIN"
        val result = pipeline.process(mock(Bitmap::class.java))
        
        val drug = result.verifiedDrugs.find { it.normalizedName == "Aspirin" }
        assertEquals(VerificationStatus.GREEN, drug?.verificationStatus)
    }

    @Test
    fun testEmptyOcr() = runBlocking {
        mockTextExtractor.textToReturn = ""
        val result = pipeline.process(mock(Bitmap::class.java))
        assertTrue(result.verifiedDrugs.isEmpty())
    }
}
