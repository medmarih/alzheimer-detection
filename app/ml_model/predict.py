import tensorflow as tf
import numpy as np
from PIL import Image
model = tf.keras.models.load_model('app/ml_model/alzheimer_model.h5')
print("Input shape du modèle :", model.input_shape)
print("Output shape du modèle :", model.output_shape)
def predict_irm(image_path):
    target_size = (128, 128)
    labels = ['Non Alzheimer', 'Very Mild Dementia', 'Mild Dementia', 'Moderate Dementia']

    # Chargement et traitement de l'image
    image = Image.open(image_path).convert('RGB')
    image = image.resize(target_size)

    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)  # Ajouter la dimension batch
    image_array = image_array                   # Normalisation

    # Prédiction
    prediction = model.predict(image_array)[0]
    print("Sortie brute du modèle :", prediction)

    # Choix de la classe prédite
    idx = np.argmax(prediction)
    confidence = prediction[idx]
    result = labels[idx]

    return result, float(confidence)
