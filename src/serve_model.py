"""
Flask API of the SMS Spam detection model model.
"""
import os
import time
from flask import Flask, jsonify, request, Response
from flasgger import Swagger
from model_loader import model_loader

# IMPORTANT: Import preprocessing functions so joblib can find them when unpickling
from text_preprocessing import _text_process, _extract_message_len

from prometheus_client import Counter, Histogram, generate_latest, REGISTRY

# Read port from environment variable, default to 8081
PORT = int(os.getenv('MODEL_SERVICE_PORT', '8081'))

# Get the version of the model
MODEL_VERSION = os.getenv('MODEL_VERSION', 'v1')

# Initialize Flask app
app = Flask(__name__)
swagger = Swagger(app)

# Load models on startup
print("="*60)
print("Starting SMS Spam Detection Model Service")
print(f"Port: {PORT}")
print("="*60)

models = model_loader.load_all_models()
preprocessor = models['preprocessor']
classifier = models['model']

print(f"\n{'='*60}")
print(f"🚀 Model Service Ready on port {PORT}")
print(f"{'='*60}\n")

# Prometheus metrics
predictions_total = Counter('model_predictions_total', 'Total predictions', ['version', 'result'])
prediction_latency_seconds = Histogram('model_prediction_latency_seconds', 'Prediction latency', ['version'])


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: Service is healthy
    """
    return jsonify({
        'status': 'healthy',
        'service': 'sms-spam-classifier',
        'port': PORT
    }), 200


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict whether an SMS is Spam.
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: message to be classified.
          required: True
          schema:
            type: object
            required: sms
            properties:
                sms:
                    type: string
                    example: This is an example of an SMS.
    responses:
      200:
        description: "The result of the classification: 'spam' or 'ham'."
    """
    start_time = time.time()

    try:
        input_data = request.get_json()
        
        if not input_data or 'sms' not in input_data:
            return jsonify({
                'error': 'Missing required field: sms',
                'example': {'sms': 'Your message here'}
            }), 400
        
        sms = input_data.get('sms')
        
        # Preprocess and predict using the loaded preprocessor
        processed_sms = preprocessor.transform([sms])
        prediction = classifier.predict(processed_sms)[0]
        
        # Get confidence if available
        confidence = None
        if hasattr(classifier, 'predict_proba'):
            probabilities = classifier.predict_proba(processed_sms)[0]
            confidence = float(max(probabilities))

        predictions_total.labels(version=MODEL_VERSION, result=prediction).inc()
        model_prediction_latency_seconds.labels(version=MODEL_VERSION).observe(time.time() - start_time)
        
        res = {
            "result": prediction,
            "classifier": "decision tree",
            "sms": sms
        }
        
        if confidence is not None:
            res['confidence'] = round(confidence, 4)
        
        print(res)
        return jsonify(res)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Prediction failed'
        }), 500


@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint - redirects to API documentation
    """
    return jsonify({
        'service': 'SMS Spam Detection Model Service',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'predict': '/predict (POST)',
            'docs': '/apidocs'
        }
    }), 200

# Endpoint for exposing prometheus metrics
@app.route('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), mimetype='text/plain')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT, debug=False)