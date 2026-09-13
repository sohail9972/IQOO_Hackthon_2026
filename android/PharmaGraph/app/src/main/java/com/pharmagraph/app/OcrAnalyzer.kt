package com.pharmagraph.app

import android.graphics.Bitmap
import android.util.Log
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.tasks.await

class OcrAnalyzer {
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    suspend fun analyzeImage(bitmap: Bitmap): List<String> {
        val image = InputImage.fromBitmap(bitmap, 0)
        Log.d("OcrAnalyzer", "Analyzing image of size: ${bitmap.width}x${bitmap.height}")
        return try {
            val result = recognizer.process(image).await()
            val extracted = extractDrugNames(result.text)
            Log.d("OcrAnalyzer", "Extracted text: ${result.text}")
            Log.d("OcrAnalyzer", "Extracted drug names: $extracted")
            extracted
        } catch (e: Exception) {
            Log.e("OcrAnalyzer", "OCR Error", e)
            emptyList()
        }
    }

    private fun extractDrugNames(text: String): List<String> {
        // Basic drug name extraction logic
        // Splits by common delimiters and filters by length
        return text.split("\n", ",", ";")
            .map { it.trim() }
            .filter { it.length >= 3 && it.any { char -> char.isLetter() } }
            .distinct()
    }
}
