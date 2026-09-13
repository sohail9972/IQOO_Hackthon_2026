package com.pharmagraph.app.infrastructure

import android.graphics.Bitmap
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import com.pharmagraph.app.domain.PrescriptionTextExtractor
import kotlinx.coroutines.tasks.await

class MlKitPrescriptionTextExtractor : PrescriptionTextExtractor {
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    override suspend fun extract(image: Bitmap): String {
        val inputImage = InputImage.fromBitmap(image, 0)
        return try {
            val result = recognizer.process(inputImage).await()
            result.text
        } catch (e: Exception) {
            ""
        }
    }
}
